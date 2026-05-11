from http import HTTPStatus

import pytest
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone

from project_rokto.blood_requests.models import BloodRequest
from project_rokto.blood_requests.models import BloodRequestDonor
from project_rokto.blood_requests.serializers import (
    BloodRequestDonorDashboardSerializer,
)
from project_rokto.blood_requests.tests.test_api import create_verified_user

pytestmark = pytest.mark.django_db


def test_reveal_contact_invalid_actor(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor1")
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Test",
        bags_needed=1,
        donation_date="2026-05-15",
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=request,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
    )

    client.force_login(seeker)
    url = reverse("api:requests-reveal-contact", kwargs={"pk": entry.pk})

    # Invalid actor type (Hits line 79 in blood_requests/views.py)
    response = client.post(url, {"actor": "invalid"})
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_accept_request_invalid_status(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor1")
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Test",
        bags_needed=1,
        donation_date="2026-05-15",
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=request,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
    )

    client.force_login(donor)
    url = reverse("api:requests-accept-request", kwargs={"pk": entry.pk})

    # Already accepted (Hits line 100-101 in blood_requests/views.py)
    response = client.post(url)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "already been responded to" in response.json()["detail"]


def test_decline_request_invalid_status(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor1")
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Test",
        bags_needed=1,
        donation_date="2026-05-15",
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=request,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.DECLINED,
    )

    client.force_login(donor)
    url = reverse("api:requests-decline-request", kwargs={"pk": entry.pk})

    # Already declined (Hits line 108-109 in blood_requests/views.py)
    response = client.post(url)
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_confirm_donation_unauthorized_user(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor1")
    other = create_verified_user(username="other")
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

    client.force_login(other)
    url = reverse("api:requests-confirm-donation", kwargs={"pk": entry.pk})

    # Unauthorized actor (Hits line 166 in blood_requests/views.py)
    response = client.post(
        url,
        {"confirmation": "YES"},
        content_type="application/json",
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_donor_response_public_view_decline(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor1")
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="H1",
        bags_needed=1,
        donation_date="2026-05-15",
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(blood_request=request, donor=donor)

    # Public view: decline
    url = reverse(
        "blood_requests:donor_response",
        kwargs={"token": entry.token, "action_type": "decline"},
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    entry.refresh_from_db()
    assert entry.response_status == BloodRequestDonor.ResponseStatus.DECLINED


def test_confirm_donation_public_view_already_confirmed(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor1")
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="H1",
        bags_needed=1,
        donation_date=timezone.now().date(),
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=request,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
        seeker_confirmation=BloodRequestDonor.DonationConfirmation.YES,
        donor_confirmation=BloodRequestDonor.DonationConfirmation.YES,
    )

    url = reverse(
        "blood_requests:confirm_donation",
        kwargs={
            "token": entry.token,
            "actor": "seeker",
            "status_type": "yes",
        },
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert "already fully confirmed" in response.content.decode()


def test_confirm_donation_public_view_invalid_actor(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor1")
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="H1",
        bags_needed=1,
        donation_date=timezone.now().date(),
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(blood_request=request, donor=donor)

    url = reverse(
        "blood_requests:confirm_donation",
        kwargs={
            "token": entry.token,
            "actor": "invalid",
            "status_type": "yes",
        },
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_donor_response_public_view_invalid_action(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor1")
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="H1",
        bags_needed=1,
        donation_date="2026-05-15",
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(blood_request=request, donor=donor)

    url = reverse(
        "blood_requests:donor_response",
        kwargs={"token": entry.token, "action_type": "invalid"},
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_model_is_fully_confirmed_false(client):
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
        seeker_confirmation=BloodRequestDonor.DonationConfirmation.YES,
        donor_confirmation=BloodRequestDonor.DonationConfirmation.PENDING,
    )
    assert entry.is_fully_confirmed is False


def test_serializer_get_phone_number_donor(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor1")
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Test",
        bags_needed=1,
        donation_date=timezone.now().date(),
        hospital="H1",
    )
    BloodRequestDonor.objects.create(
        blood_request=request,
        donor=donor,
        seeker_contact_accessed_at=timezone.now(),
    )

    client.force_login(donor)
    url = reverse("api:requests-received-requests")
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data[0]["phone_number"] == seeker.phone_number


def test_serializer_get_phone_number_none(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor1")
    other = create_verified_user(username="other")
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Test",
        bags_needed=1,
        donation_date=timezone.now().date(),
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(blood_request=request, donor=donor)

    rf = RequestFactory()
    req = rf.get("/")
    req.user = other

    serializer = BloodRequestDonorDashboardSerializer(entry, context={"request": req})
    assert serializer.data["phone_number"] is None
