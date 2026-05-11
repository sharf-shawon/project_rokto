import datetime
from http import HTTPStatus
from typing import cast

import pytest
from django.urls import reverse

from project_rokto.blood_requests.models import BloodRequest
from project_rokto.blood_requests.models import BloodRequestDonor
from project_rokto.users.models import NIDVerification
from project_rokto.users.models import User
from project_rokto.users.tests.factories import NIDVerificationFactory
from project_rokto.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def create_verified_user(**kwargs):
    user = cast("User", UserFactory(is_phone_verified=True, **kwargs))
    NIDVerificationFactory(user=user, status=NIDVerification.Status.VERIFIED)
    return user


def test_submit_blood_request_success(client):
    seeker = create_verified_user()
    client.force_login(seeker)

    donors = [cast("User", UserFactory()) for _ in range(3)]
    donor_ids = [d.id for d in donors]

    url = reverse("api:requests-list")
    payload = {
        "reason": "Accident",
        "bags_needed": 2,
        "donation_date": "2026-05-15",
        "hospital": "Square Hospital",
        "donor_ids": donor_ids,
    }

    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == HTTPStatus.CREATED

    assert BloodRequest.objects.filter(seeker=seeker).exists()
    expected_donor_count = 3
    assert (
        BloodRequestDonor.objects.filter(blood_request__seeker=seeker).count()
        == expected_donor_count
    )


def test_submit_blood_request_rate_limit(client):
    seeker = create_verified_user()
    client.force_login(seeker)

    donor = cast("User", UserFactory())
    url = reverse("api:requests-list")
    payload = {
        "reason": "First",
        "bags_needed": 1,
        "donation_date": "2026-05-15",
        "hospital": "H1",
        "donor_ids": [donor.id],
    }

    # First request
    response1 = client.post(url, payload, content_type="application/json")
    assert response1.status_code == HTTPStatus.CREATED

    # Immediate second request
    response2 = client.post(url, payload, content_type="application/json")
    assert response2.status_code == HTTPStatus.BAD_REQUEST
    assert "one blood donation request every 30 minutes" in str(response2.json())


def test_submit_blood_request_max_donors(client):
    seeker = create_verified_user()
    client.force_login(seeker)

    donors = [cast("User", UserFactory()) for _ in range(5)]
    donor_ids = [d.id for d in donors]

    url = reverse("api:requests-list")
    payload = {
        "reason": "Too many",
        "bags_needed": 1,
        "donation_date": "2026-05-15",
        "hospital": "H1",
        "donor_ids": donor_ids,
    }

    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_donor_response_accept(client):
    seeker = cast("User", UserFactory(phone_number="01711111111"))
    donor = cast("User", UserFactory(phone_number="01822222222"))
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
        kwargs={"token": entry.token, "action_type": "accept"},
    )
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    entry.refresh_from_db()
    assert entry.response_status == BloodRequestDonor.ResponseStatus.ACCEPTED


def test_post_donation_confirmation_updates_profile(client):
    seeker = cast("User", UserFactory())
    donor = cast("User", UserFactory(last_donation_date=None))
    donation_date = datetime.date(2026, 5, 1)
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="H1",
        bags_needed=1,
        donation_date=donation_date,
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=request,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
    )

    # 1. Seeker confirms YES
    url_seeker = reverse(
        "blood_requests:confirm_donation",
        kwargs={
            "token": entry.token,
            "actor": "seeker",
            "status_type": "yes",
        },
    )
    response = client.get(url_seeker)
    assert response.status_code == HTTPStatus.OK

    donor.refresh_from_db()
    assert donor.last_donation_date is None  # Not yet fully confirmed

    # 2. Donor confirms YES
    url_donor = reverse(
        "blood_requests:confirm_donation",
        kwargs={
            "token": entry.token,
            "actor": "donor",
            "status_type": "yes",
        },
    )
    response = client.get(url_donor)
    assert response.status_code == HTTPStatus.OK

    donor.refresh_from_db()
    assert donor.last_donation_date == donation_date  # Now fully confirmed


def test_reveal_contact_privacy(client):
    seeker = create_verified_user()
    donor = cast("User", UserFactory(phone_number="01822222222"))
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="H1",
        bags_needed=1,
        donation_date="2026-05-15",
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=request,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
    )

    url = reverse("api:requests-reveal-contact", kwargs={"pk": entry.pk})

    # 1. Unauthenticated
    response = client.post(url, {"actor": "seeker"})
    assert response.status_code == HTTPStatus.FORBIDDEN

    client.force_login(seeker)

    # 2. Unauthorized actor (e.g. random user)
    other_user = create_verified_user(username="other")
    client.force_login(other_user)
    response = client.post(url, {"actor": "seeker"})
    assert response.status_code == HTTPStatus.FORBIDDEN

    # 3. Authorized Seeker reveal
    client.force_login(seeker)
    response = client.post(url, {"actor": "seeker"})
    assert response.status_code == HTTPStatus.OK
    assert response.json()["phone_number"] == "01822222222"

    entry.refresh_from_db()
    assert entry.donor_contact_accessed_at is not None


def test_sent_requests_list(client):
    seeker = create_verified_user()
    client.force_login(seeker)

    num_donors = 2
    donors = [cast("User", UserFactory()) for _ in range(num_donors)]
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Test",
        bags_needed=1,
        donation_date="2026-05-15",
        hospital="H1",
    )
    for d in donors:
        BloodRequestDonor.objects.create(blood_request=request, donor=d)

    url = reverse("api:requests-sent-requests")
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["hospital"] == "H1"
    assert len(data[0]["donors"]) == num_donors


def test_received_requests_list(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor_user")
    client.force_login(donor)

    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Test",
        bags_needed=1,
        donation_date="2026-05-15",
        hospital="H2",
    )
    BloodRequestDonor.objects.create(blood_request=request, donor=donor)

    url = reverse("api:requests-received-requests")
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["blood_request"]["hospital"] == "H2"
    assert data[0]["seeker_name"] is not None
