from typing import TYPE_CHECKING
from typing import cast
from unittest.mock import patch

import pytest
from django.urls import reverse

from project_rokto.donors.models import Donor
from project_rokto.organizations.models import NotificationQuota
from project_rokto.organizations.models import Organization
from project_rokto.organizations.models import OrganizationMember
from project_rokto.organizations.services import DonorImportService
from project_rokto.organizations.tasks import send_donor_invite
from project_rokto.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from project_rokto.users.models import User

pytestmark = pytest.mark.django_db


def test_full_flow_import_invite_signup_quota(client):
    # 1. Setup Org and Quota
    org = Organization.objects.create(name="Sandhani")
    admin = cast("User", UserFactory(is_phone_verified=True))
    org.members.create(user=admin, role=OrganizationMember.Role.ADMIN)

    # Setup global quota too as it's checked first
    NotificationQuota.objects.get_or_create(
        organization=None,
        channel=NotificationQuota.Channel.SMS,
        defaults={"daily_limit": 100},
    )

    NotificationQuota.objects.create(
        organization=org, channel=NotificationQuota.Channel.SMS, daily_limit=5
    )

    # 2. Bulk Import
    csv_content = (
        "phone_number,name,blood_group\n"
        "01711111111,John Doe,A+\n"
        "01722222222,Jane Doe,B+"
    )
    DonorImportService.import_from_csv(org, csv_content.encode())

    # 3 donors: admin (created by factory) + 2 from CSV
    expected_donor_count = 3
    assert Donor.objects.count() == expected_donor_count
    donor1 = Donor.objects.get(phone_number="01711111111")

    # 3. Send Invite (within quota)
    with patch("project_rokto.notifications.backends.MiMSMSBackend.send") as mock_send:
        mock_send.return_value = {"status": "sent", "trxn_id": "123"}
        success, reason = send_donor_invite(donor1.id, org.id)
        assert success is True

    # 4. Attempt second invite (User Cool-off)
    success, reason = send_donor_invite(donor1.id, org.id)
    assert success is False
    assert "Cool-off" in reason

    # 5. Signup (Identity Promotion)
    session = client.session
    session["verified_phone_number"] = "01711111111"
    session.save()

    url = reverse("users:signup_info")
    client.post(url, {"name": "Verified John", "email": "john@example.com"})

    donor1.refresh_from_db()
    assert donor1.user is not None
    assert donor1.invite_status == Donor.InviteStatus.REGISTERED
