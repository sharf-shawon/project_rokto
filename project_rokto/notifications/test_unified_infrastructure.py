from http import HTTPStatus
from typing import cast

import pytest
from django.urls import reverse

from project_rokto.notifications.models import NotificationLog
from project_rokto.notifications.models import SMSLog
from project_rokto.notifications.services import UnifiedNotificationService
from project_rokto.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_unified_notification_service_sms_dual_logging():
    """Test that SMS sending creates both NotificationLog and SMSLog."""
    user = UserFactory(phone_number="01712345678")
    donor = user.donor_profile

    UnifiedNotificationService.send(
        channel="SMS", message="Test Message", category=SMSLog.Category.OTP, donor=donor
    )

    # Check NotificationLog
    assert NotificationLog.objects.count() == 1
    log = cast("NotificationLog", NotificationLog.objects.first())
    assert log.channel == "SMS"
    assert log.category == "OTP"
    assert log.donor == donor

    # Check SMSLog
    assert SMSLog.objects.count() == 1
    sms_log = cast("SMSLog", SMSLog.objects.first())
    assert sms_log.phone_number == "01712345678"
    assert sms_log.category == "OTP"


def test_unified_notification_service_email_logging():
    """Test that Email sending creates NotificationLog."""
    user = UserFactory(email="test@example.com")
    donor = user.donor_profile

    UnifiedNotificationService.send(channel="EMAIL", message="Test Email", donor=donor)

    assert NotificationLog.objects.count() == 1
    log = cast("NotificationLog", NotificationLog.objects.first())
    assert log.channel == "EMAIL"
    assert log.status == "SENT"


def test_phone_login_otp_visibility_in_logs(client):
    """Integration test: OTP request should appear in NotificationLog."""
    url = reverse("users:phone_login")
    response = client.post(url, {"phone_number": "01711112222"})
    assert response.status_code == HTTPStatus.FOUND

    # Check NotificationLog
    assert NotificationLog.objects.filter(category="OTP").exists()
    log = NotificationLog.objects.get(category="OTP")
    assert log.channel == "SMS"
    assert (
        "01711112222" in str(log.donor) if log.donor else True
    )  # Donor might not exist yet for new user


def test_log_failure_method():
    """Test the log_failure utility."""
    UnifiedNotificationService.log_failure(
        channel="SMS",
        category=SMSLog.Category.EMERGENCY,
        donor=None,
        organization=None,
        reason="Quota Exceeded",
    )

    assert NotificationLog.objects.filter(status="BLOCKED").exists()
    log = NotificationLog.objects.get(status="BLOCKED")
    assert log.failure_reason == "Quota Exceeded"
