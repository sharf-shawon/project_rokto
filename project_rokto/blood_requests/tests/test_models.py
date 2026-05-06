from typing import TYPE_CHECKING
from typing import cast

import pytest

from project_rokto.blood_requests.models import BloodRequest
from project_rokto.blood_requests.models import BloodRequestDonor
from project_rokto.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from project_rokto.users.models import User

pytestmark = pytest.mark.django_db


def test_blood_request_creation():
    seeker = cast("User", UserFactory())
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Emergency",
        bags_needed=2,
        donation_date="2026-05-10",
        hospital="DMC",
    )
    assert request.seeker == seeker
    assert str(request) == f"Request by {seeker.username} for 2026-05-10"


def test_blood_request_donor_creation():
    seeker = cast("User", UserFactory())
    donor = cast("User", UserFactory())
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Emergency",
        bags_needed=1,
        donation_date="2026-05-10",
        hospital="DMC",
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=request,
        donor=donor,
    )
    assert entry.blood_request == request
    assert entry.donor == donor
    assert entry.response_status == BloodRequestDonor.ResponseStatus.PENDING
    assert entry.token is not None
