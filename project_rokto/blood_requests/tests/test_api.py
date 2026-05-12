import datetime
from http import HTTPStatus
from typing import cast

import pytest
from django.urls import reverse
from django.utils import timezone

from project_rokto.blood_requests.models import BloodRequest
from project_rokto.blood_requests.models import BloodRequestDonor
from project_rokto.users.models import NIDVerification
from project_rokto.users.models import User
from project_rokto.users.tests.factories import NIDVerificationFactory
from project_rokto.users.tests.factories import UserFactory


def create_verified_user(**kwargs):
    user = cast("User", UserFactory(is_phone_verified=True, **kwargs))
    NIDVerificationFactory(user=user, status=NIDVerification.Status.VERIFIED)
    return user


@pytest.mark.django_db
def test_blood_request_flow(client):
    seeker = create_verified_user()
    donor = cast("User", UserFactory())
    donation_date = timezone.now().date() + datetime.timedelta(days=1)

    client.force_login(seeker)

    url = reverse("api:requests-list")
    data = {
        "reason": "Emergency surgery",
        "bags_needed": 2,
        "donation_date": donation_date.strftime("%Y-%m-%d"),
        "hospital": "City Hospital",
        "donor_ids": [str(donor.id)],
    }

    response = client.post(url, data, content_type="application/json")
    assert response.status_code == HTTPStatus.CREATED

    # Check model creation
    request = BloodRequest.objects.get(seeker=seeker)
    assert request.hospital == "City Hospital"
    assert request.donors.count() == 1

    entry = request.donors.first()
    assert entry is not None
    assert entry.donor == donor
    assert entry.response_status == BloodRequestDonor.ResponseStatus.PENDING

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

    donor.donor_profile.refresh_from_db()
    assert donor.donor_profile.last_donation_date is None  # Not yet fully confirmed

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

    donor.donor_profile.refresh_from_db()
    assert (
        donor.donor_profile.last_donation_date == donation_date
    )  # Now fully confirmed


@pytest.mark.django_db
def test_reveal_contact_privacy(client):
    seeker = create_verified_user()
    donor = cast("User", UserFactory(phone_number="01822222222"))
    request = BloodRequest.objects.create(
        seeker=seeker,
        hospital="Test Clinic",
        donation_date=timezone.now().date(),
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=request,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.PENDING,
    )

    url = reverse("api:requests-reveal-contact", kwargs={"pk": entry.pk})
    client.force_login(seeker)

    # Cannot reveal if pending
    response = client.post(url, {"actor": "seeker"})
    assert response.status_code == HTTPStatus.BAD_REQUEST

    # Accept request
    entry.response_status = BloodRequestDonor.ResponseStatus.ACCEPTED
    entry.save()

    # Can reveal now
    response = client.post(url, {"actor": "seeker"})
    assert response.status_code == HTTPStatus.OK
    assert response.json()["phone_number"] == donor.phone_number
