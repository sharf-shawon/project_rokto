import datetime
from http import HTTPStatus

import pytest
from django.urls import reverse
from django.utils import timezone

from project_rokto.blood_requests.models import BloodRequest
from project_rokto.blood_requests.models import BloodRequestDonor
from project_rokto.blood_requests.tests.test_api import create_verified_user

pytestmark = pytest.mark.django_db


def test_accept_request_api(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor1")
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Test",
        bags_needed=1,
        donation_date="2026-05-15",
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(blood_request=request, donor=donor)

    client.force_login(donor)
    url = reverse("api:requests-accept-request", kwargs={"pk": entry.pk})
    response = client.post(url)

    assert response.status_code == HTTPStatus.OK
    entry.refresh_from_db()
    assert entry.response_status == BloodRequestDonor.ResponseStatus.ACCEPTED


def test_decline_request_api(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor1")
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Test",
        bags_needed=1,
        donation_date="2026-05-15",
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(blood_request=request, donor=donor)

    client.force_login(donor)
    url = reverse("api:requests-decline-request", kwargs={"pk": entry.pk})
    response = client.post(url)

    assert response.status_code == HTTPStatus.OK
    entry.refresh_from_db()
    assert entry.response_status == BloodRequestDonor.ResponseStatus.DECLINED


def test_confirm_donation_api(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor1")
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Test",
        bags_needed=1,
        donation_date=timezone.now().date(),
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=request,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
    )

    client.force_login(seeker)
    url = reverse("api:requests-confirm-donation", kwargs={"pk": entry.pk})
    response = client.post(
        url,
        {"confirmation": "YES"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.OK
    entry.refresh_from_db()
    assert entry.seeker_confirmation == BloodRequestDonor.DonationConfirmation.YES

    # Now donor confirms NO
    client.force_login(donor)
    response = client.post(url, {"confirmation": "NO"}, content_type="application/json")
    assert response.status_code == HTTPStatus.OK
    entry.refresh_from_db()
    assert entry.donor_confirmation == BloodRequestDonor.DonationConfirmation.NO


def test_cancel_request_api(client):
    seeker = create_verified_user()
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Test",
        bags_needed=1,
        donation_date="2026-05-15",
        hospital="H1",
    )

    client.force_login(seeker)
    url = reverse("api:requests-cancel-request", kwargs={"pk": request.pk})
    response = client.post(url)

    assert response.status_code == HTTPStatus.OK
    assert not BloodRequest.objects.filter(pk=request.pk).exists()


def test_serializer_can_confirm(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor1")

    # Past request, accepted
    req_past = BloodRequest.objects.create(
        seeker=seeker,
        reason="Past",
        bags_needed=1,
        donation_date=timezone.now().date() - datetime.timedelta(days=1),
        hospital="H1",
    )
    BloodRequestDonor.objects.create(
        blood_request=req_past,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
    )

    # Future request, accepted
    req_future = BloodRequest.objects.create(
        seeker=seeker,
        reason="Future",
        bags_needed=1,
        donation_date=timezone.now().date() + datetime.timedelta(days=1),
        hospital="H2",
    )
    BloodRequestDonor.objects.create(
        blood_request=req_future,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
    )

    # Past request, pending
    req_pending = BloodRequest.objects.create(
        seeker=seeker,
        reason="Pending",
        bags_needed=1,
        donation_date=timezone.now().date() - datetime.timedelta(days=1),
        hospital="H3",
    )
    BloodRequestDonor.objects.create(
        blood_request=req_pending,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.PENDING,
    )

    client.force_login(donor)
    url = reverse("api:requests-received-requests")
    response = client.get(url)

    data = response.json()
    # received_requests is ordered by -blood_request__created_at
    # Let's find each by hospital name

    def find_entry(hospital):
        for d in data:
            if d["blood_request"]["hospital"] == hospital:
                return d
        return None

    assert find_entry("H1")["can_confirm"] is True
    assert find_entry("H2")["can_confirm"] is False
    assert find_entry("H3")["can_confirm"] is False
