from typing import TYPE_CHECKING
from typing import cast
from unittest.mock import patch

import pytest
from django.core.cache import cache

from project_rokto.organizations.models import NotificationQuota
from project_rokto.organizations.models import Organization
from project_rokto.organizations.services import NotificationDispatcher
from project_rokto.organizations.services import SMSService
from project_rokto.users.models import NotificationPreference
from project_rokto.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from project_rokto.users.models import User


pytestmark = pytest.mark.django_db


def test_dispatcher_respects_preferences(client):
    user = cast("User", UserFactory())
    prefs, _ = NotificationPreference.objects.get_or_create(user=user)

    # Disable SMS
    prefs.sms_enabled = False
    prefs.save()

    with (
        patch("project_rokto.organizations.tasks.send_sms_task.delay") as mock_sms,
        patch("project_rokto.organizations.tasks.send_email_task.delay") as mock_email,
    ):
        NotificationDispatcher.send(user, "emergency_request", {"hospital": "Test"})

        # SMS should NOT be called
        mock_sms.assert_not_called()
        # Email should be called (default enabled)
        mock_email.assert_called_once()


def test_dispatcher_quota_enforcement():
    org = Organization.objects.create(name="Limited Org")
    user = UserFactory()

    # Create a quota with 0 limit
    NotificationQuota.objects.create(
        organization=org, channel=NotificationQuota.Channel.SMS, daily_limit=0
    )

    # Attempt to send SMS directly via SMSService to check quota return
    success, reason = SMSService.send(
        user, "emergency_request", {"hospital": "Test"}, organization=org
    )

    assert success is False
    assert "quota exceeded" in reason


def test_dispatcher_user_cooloff():
    cache.clear()

    user = UserFactory()
    org = Organization.objects.create(name="Cooloff Org")

    # First send success
    with patch("project_rokto.notifications.backends.MiMSMSBackend.send") as mock_send:
        mock_send.return_value = {"status": "sent", "trxn_id": "123"}

        success, _ = SMSService.send(
            user, "emergency_request", {"hospital": "Test"}, organization=org
        )
        assert success is True

        # Second send within 24h should be blocked by cool-off
        success, reason = SMSService.send(
            user, "emergency_request", {"hospital": "Test"}, organization=org
        )
        assert success is False
        assert "Cool-off" in reason
