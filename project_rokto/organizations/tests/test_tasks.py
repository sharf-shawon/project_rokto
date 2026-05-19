import uuid
from unittest.mock import patch

import pytest

from project_rokto.donors.models import Donor
from project_rokto.organizations.models import NotificationQuota
from project_rokto.organizations.models import Organization
from project_rokto.organizations.tasks import send_donor_invite

pytestmark = pytest.mark.django_db


def test_send_donor_invite_not_found():
    success, reason = send_donor_invite(uuid.uuid4(), uuid.uuid4())
    assert success is False
    assert reason == "Donor or Organization not found"


def test_send_donor_invite_quota_blocked():
    org = Organization.objects.create(name="Blocked Org")
    donor = Donor.objects.create(phone_number="01700000000")

    # Create a quota with 0 limit to force block
    NotificationQuota.objects.create(
        organization=org, channel=NotificationQuota.Channel.SMS, daily_limit=0
    )

    with patch("project_rokto.notifications.backends.MiMSMSBackend.send") as mock_send:
        mock_send.return_value = {"status": "sent", "trxn_id": "123"}
        success, reason = send_donor_invite(donor.id, org.id)
        assert success is False
        assert "quota exceeded" in reason


def test_send_donor_invite_success():
    org = Organization.objects.create(name="Success Org")
    donor = Donor.objects.create(phone_number="01799999999")
    org.refresh_from_db()
    donor.refresh_from_db()

    NotificationQuota.objects.get_or_create(
        organization=None,
        channel=NotificationQuota.Channel.SMS,
        defaults={"daily_limit": 100},
    )

    NotificationQuota.objects.create(
        organization=org, channel=NotificationQuota.Channel.SMS, daily_limit=10
    )

    with patch("project_rokto.notifications.backends.MiMSMSBackend.send") as mock_send:
        mock_send.return_value = {"status": "sent", "trxn_id": "123"}
        success, reason = send_donor_invite(donor.id, org.id)
        assert success is True
        assert "SMS sent successfully" in reason

    donor.refresh_from_db()
    assert donor.invite_status == Donor.InviteStatus.SENT


def test_send_donor_invite_global_quota_blocked():
    org = Organization.objects.create(name="Org")
    donor = Donor.objects.create(phone_number="01722222222")

    # Force global quota block
    NotificationQuota.objects.update_or_create(
        organization=None,
        channel=NotificationQuota.Channel.SMS,
        defaults={"daily_limit": 0},
    )

    with patch("project_rokto.notifications.backends.MiMSMSBackend.send") as mock_send:
        mock_send.return_value = {"status": "sent", "trxn_id": "123"}
        success, reason = send_donor_invite(donor.id, org.id)
        assert success is False
        assert "Global quota exceeded" in reason


def test_send_donor_invite_exception():
    org = Organization.objects.create(name="Fail Org")
    donor = Donor.objects.create(phone_number="01788888888")
    org.refresh_from_db()
    donor.refresh_from_db()

    NotificationQuota.objects.update_or_create(
        organization=None,
        channel=NotificationQuota.Channel.SMS,
        defaults={"daily_limit": 100},
    )

    NotificationQuota.objects.create(
        organization=org, channel=NotificationQuota.Channel.SMS, daily_limit=10
    )

    with patch("project_rokto.notifications.backends.MiMSMSBackend.send") as mock_send:
        mock_send.side_effect = Exception("Boom")
        success, reason = send_donor_invite(donor.id, org.id)
        assert success is False
        assert reason == "Boom"

        # Verify log
        assert donor.notification_logs.filter(status="FAILED").exists()
