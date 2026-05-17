from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import cast

import pytest
from django.urls import reverse
from django.utils import timezone

from project_rokto.blood_requests.models import BloodRequest
from project_rokto.blood_requests.models import BloodRequestDonor
from project_rokto.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from project_rokto.users.models import User

pytestmark = pytest.mark.django_db


def test_web_confirmation_updates_profile(client):
    seeker = cast("User", UserFactory())
    donor = cast("User", UserFactory())
    donor.donor_profile.last_donation_date = None
    donor.donor_profile.save()

    request_date = timezone.now().date()
    blood_request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Test",
        bags_needed=1,
        donation_date=request_date,
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=blood_request,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
        seeker_confirmation=BloodRequestDonor.DonationConfirmation.YES,
    )

    # Donor confirms YES via web view
    url = reverse(
        "blood_requests:confirm_donation",
        kwargs={"token": entry.token, "actor": "donor", "status_type": "yes"},
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    donor.donor_profile.refresh_from_db()
    assert donor.donor_profile.last_donation_date == request_date


def test_web_confirmation_idempotency(client):
    seeker = cast("User", UserFactory())
    donor = cast("User", UserFactory())
    request_date = timezone.now().date()

    donor.donor_profile.last_donation_date = request_date
    donor.donor_profile.save()

    blood_request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Test",
        bags_needed=1,
        donation_date=request_date,
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=blood_request,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
        seeker_confirmation=BloodRequestDonor.DonationConfirmation.YES,
        donor_confirmation=BloodRequestDonor.DonationConfirmation.YES,
    )

    # Re-confirming via web view
    url = reverse(
        "blood_requests:confirm_donation",
        kwargs={"token": entry.token, "actor": "donor", "status_type": "yes"},
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    donor.donor_profile.refresh_from_db()
    assert donor.donor_profile.last_donation_date == request_date
