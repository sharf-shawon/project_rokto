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


def test_confirmation_record_timestamps_and_lock(client):
    seeker = cast("User", UserFactory())
    donor = cast("User", UserFactory())
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

    # 1. Seeker confirms via API
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
    assert entry.seeker_confirmation_at is not None

    # 2. Try to change seeker confirmation -> should fail
    response = client.post(url, {"confirmation": "NO"}, content_type="application/json")
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "already confirmed" in response.json()["detail"]

    # 3. Donor confirms via API
    client.force_login(donor)
    response = client.post(
        url,
        {"confirmation": "YES"},
        content_type="application/json",
    )
    assert response.status_code == HTTPStatus.OK

    entry.refresh_from_db()
    assert entry.donor_confirmation == BloodRequestDonor.DonationConfirmation.YES
    assert entry.donor_confirmation_at is not None
    assert entry.is_fully_confirmed is True


def test_full_confirmation_required_for_profile_update(client):
    seeker = cast("User", UserFactory())
    donor = cast("User", UserFactory(last_donation_date=None))
    request_date = timezone.now().date()
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Test",
        bags_needed=1,
        donation_date=request_date,
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=request,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
    )

    # Seeker confirms YES
    client.force_login(seeker)
    url = reverse("api:requests-confirm-donation", kwargs={"pk": entry.pk})
    client.post(url, {"confirmation": "YES"}, content_type="application/json")

    donor.donor_profile.refresh_from_db()
    assert donor.donor_profile.last_donation_date is None  # Not yet fully confirmed

    # Donor confirms YES
    client.force_login(donor)
    client.post(url, {"confirmation": "YES"}, content_type="application/json")

    donor.donor_profile.refresh_from_db()
    assert donor.donor_profile.last_donation_date == request_date  # Now fully confirmed


def test_user_confirmed_stats(client):
    seeker = cast("User", UserFactory())
    donor = cast("User", UserFactory())
    request_date = timezone.now().date()
    expected_confirmed_count = 2

    # Request 1: Fully confirmed
    req1 = BloodRequest.objects.create(
        seeker=seeker,
        reason="R1",
        bags_needed=1,
        donation_date=request_date,
        hospital="H1",
    )
    BloodRequestDonor.objects.create(
        blood_request=req1,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
        seeker_confirmation=BloodRequestDonor.DonationConfirmation.YES,
        donor_confirmation=BloodRequestDonor.DonationConfirmation.YES,
    )

    # Request 2: Only seeker confirmed
    req2 = BloodRequest.objects.create(
        seeker=seeker,
        reason="R2",
        bags_needed=1,
        donation_date=request_date,
        hospital="H2",
    )
    entry2 = BloodRequestDonor.objects.create(
        blood_request=req2,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
        seeker_confirmation=BloodRequestDonor.DonationConfirmation.YES,
        donor_confirmation=BloodRequestDonor.DonationConfirmation.PENDING,
    )

    assert donor.total_donations_confirmed == 1
    assert seeker.total_received_confirmed == 1

    # Donor confirms Request 2
    entry2.donor_confirmation = BloodRequestDonor.DonationConfirmation.YES
    entry2.save()

    assert donor.total_donations_confirmed == expected_confirmed_count
    assert seeker.total_received_confirmed == expected_confirmed_count
