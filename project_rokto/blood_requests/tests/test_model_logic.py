import datetime
from typing import TYPE_CHECKING
from typing import cast

import pytest
from django.utils import timezone

from project_rokto.blood_requests.models import BloodRequest
from project_rokto.blood_requests.models import BloodRequestDonor
from project_rokto.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from project_rokto.users.models import User

pytestmark = pytest.mark.django_db


def test_donor_profile_updates_on_save():
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
        hospital="Test Hospital",
    )

    entry = BloodRequestDonor.objects.create(
        blood_request=blood_request,
        donor=donor,
    )

    # Confirming via model save
    entry.seeker_confirmation = BloodRequestDonor.DonationConfirmation.YES
    entry.donor_confirmation = BloodRequestDonor.DonationConfirmation.YES
    entry.save()

    donor.donor_profile.refresh_from_db()
    assert donor.donor_profile.last_donation_date == request_date


def test_donor_profile_does_not_regress_date():
    seeker = cast("User", UserFactory())
    future_date = timezone.now().date() + datetime.timedelta(days=10)
    past_date = timezone.now().date()

    donor = cast("User", UserFactory())
    donor.donor_profile.last_donation_date = future_date
    donor.donor_profile.save()

    blood_request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Past Request",
        bags_needed=1,
        donation_date=past_date,
        hospital="Test Hospital",
    )

    entry = BloodRequestDonor.objects.create(
        blood_request=blood_request,
        donor=donor,
    )

    entry.seeker_confirmation = BloodRequestDonor.DonationConfirmation.YES
    entry.donor_confirmation = BloodRequestDonor.DonationConfirmation.YES
    entry.save()

    donor.donor_profile.refresh_from_db()
    assert donor.donor_profile.last_donation_date == future_date
