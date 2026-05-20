import logging
import re

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils.module_loading import import_string

from .backends import MiMSMSBackend
from .models import NotificationLog
from .models import ShortURL
from .models import SMSLog
from .rate_limiter import check_otp_rate_limit
from .url_shortener import shorten_url

logger = logging.getLogger(__name__)

MAX_SMS_LENGTH = 160
SMS_ALERT_THRESHOLD = getattr(settings, "SMS_ALERT_THRESHOLD", 140)
URL_PATTERN = re.compile(r"https?://[^\s]+")


class UnifiedNotificationService:
    """
    Centralized gate for all system communications (SMS, Email, WebPush).
    Ensures consistent logging and dispatch.
    """

    @staticmethod
    def send(  # noqa: PLR0913
        channel: str,
        message: str,
        phone_number: str | None = None,
        recipient_email: str | None = None,
        category: str = SMSLog.Category.OTHER,
        donor=None,
        organization=None,
        metadata: dict | None = None,
    ) -> tuple[bool, str]:
        """Main entry point for sending notifications."""
        if channel == "SMS":
            return UnifiedNotificationService._dispatch_sms(
                message, phone_number, category, donor, organization
            )

        log = NotificationLog.objects.create(
            channel=channel,
            category=category,
            donor=donor,
            organization=organization,
            status=SMSLog.Status.SENT,
            metadata=metadata,
        )

        success, reason = False, ""
        if channel == "EMAIL":
            success, reason = UnifiedNotificationService._dispatch_email(message, donor)
        elif channel == "WEBPUSH":
            success, reason = UnifiedNotificationService._dispatch_webpush(
                message, donor
            )

        if success:
            UnifiedNotificationService.handle_success(organization, donor, channel)
        else:
            log.status = SMSLog.Status.FAILED
            log.failure_reason = reason
            log.save(update_fields=["status", "failure_reason"])

        return success, reason

    @staticmethod
    def _dispatch_sms(message, phone_number, category, donor, organization):
        if not phone_number and donor:
            phone_number = donor.phone_number

        if not phone_number:
            return False, "No phone number provided for SMS"

        return UnifiedSMSService.send(
            phone_number=phone_number,
            message=message,
            category=category,
            related_user=donor.user if donor else None,
            related_organization=organization,
        )

    @staticmethod
    def _dispatch_email(message, donor):
        EmailService = import_string(
            "project_rokto.organizations.services.EmailService"
        )

        user = donor.user if donor else None
        if not user:
            return False, "No user found for email notification"
        try:
            EmailService.send(user, "notification", {"message": message}, donor=donor)
        except Exception as e:  # noqa: BLE001
            return False, str(e)
        else:
            return True, "Email sent"

    @staticmethod
    def _dispatch_webpush(message, donor):
        WebPushService = import_string(
            "project_rokto.organizations.services.WebPushService"
        )

        user = donor.user if donor else None
        if not user:
            return False, "No user found for push notification"
        try:
            WebPushService.send(user, "notification", {"message": message}, donor=donor)
        except Exception as e:  # noqa: BLE001
            return False, str(e)
        else:
            return True, "WebPush sent"

    @staticmethod
    def handle_success(organization, donor, channel):
        """Updates usage counters and sets cool-off."""
        NotificationQuota = import_string(
            "project_rokto.organizations.models.NotificationQuota"
        )

        if donor and donor.phone_number:
            cache_key = f"cooloff:{donor.phone_number}:{channel}"
            cache.set(cache_key, True, timeout=86400)  # noqa: FBT003

        NotificationQuota.objects.filter(
            organization__isnull=True, channel=channel
        ).update(
            current_daily_usage=models.F("current_daily_usage") + 1,
            current_weekly_usage=models.F("current_weekly_usage") + 1,
            current_monthly_usage=models.F("current_monthly_usage") + 1,
        )
        if organization:
            NotificationQuota.objects.filter(
                organization=organization, channel=channel
            ).update(
                current_daily_usage=models.F("current_daily_usage") + 1,
                current_weekly_usage=models.F("current_weekly_usage") + 1,
                current_monthly_usage=models.F("current_monthly_usage") + 1,
            )

    @staticmethod
    def log_failure(channel, category, donor, organization, reason):
        """Manually log a failure (e.g., blocked by quota)."""
        NotificationLog.objects.create(
            channel=channel,
            category=category,
            donor=donor,
            organization=organization,
            status=SMSLog.Status.BLOCKED,
            failure_reason=reason,
        )

    @staticmethod
    def send_otp(phone_number, otp_code, donor=None):
        """Convenience method for sending OTP."""
        message = UnifiedSMSService.format_otp_message(otp_code)
        return UnifiedNotificationService.send(
            channel="SMS",
            phone_number=phone_number,
            message=message,
            category=SMSLog.Category.OTP,
            donor=donor,
        )


class UnifiedSMSService:
    """Centralized SMS sending service."""

    @staticmethod
    def send(
        phone_number: str,
        message: str,
        category: str = SMSLog.Category.OTHER,
        related_user=None,
        related_organization=None,
    ) -> tuple[bool, str]:
        """Send an SMS through the configured provider."""
        from project_rokto.donors.models import Donor  # noqa: PLC0415

        donor = None
        if related_user:
            donor = getattr(related_user, "donor_profile", None)
        if not donor:
            donor = Donor.objects.filter(phone_number=phone_number).first()

        log = NotificationLog.objects.create(
            channel="SMS",
            category=category,
            donor=donor,
            organization=related_organization,
            status=SMSLog.Status.SENT,
        )

        if "http" in message:
            message = UnifiedSMSService._shorten_urls_in_message(message)

        # Rate Limit Check
        extra = {"user": related_user, "org": related_organization}
        allowed, error_msg = UnifiedSMSService._check_rate_limit(
            phone_number, message, category, log, extra
        )
        if not allowed:
            return False, error_msg

        # Truncation logic
        truncated = False
        original_length = len(message)
        if original_length > MAX_SMS_LENGTH:
            truncated = True
            message = UnifiedSMSService._truncate_message(message)

        status, provider_response, failure_reason = UnifiedSMSService._dispatch(
            phone_number, message, truncated
        )

        # Update logs
        if status == SMSLog.Status.FAILED:
            log.status = SMSLog.Status.FAILED
            log.failure_reason = failure_reason
            log.save(update_fields=["status", "failure_reason"])
        elif truncated:
            log.status = SMSLog.Status.TRUNCATED
            log.save(update_fields=["status"])

        SMSLog.objects.create(
            phone_number=phone_number,
            message=message,
            original_length=original_length if truncated else None,
            category=category,
            status=status,
            failure_reason=failure_reason,
            provider_response=provider_response,
            related_user=related_user,
            related_organization=related_organization,
        )

        if status == SMSLog.Status.SENT:
            UnifiedNotificationService.handle_success(
                related_organization, donor, "SMS"
            )

        if status in (SMSLog.Status.SENT, SMSLog.Status.TRUNCATED):
            return True, "SMS sent successfully."
        return False, failure_reason or "SMS sending failed."

    @staticmethod
    def _check_rate_limit(phone_number, message, category, log, extra=None):
        if category == SMSLog.Category.OTP and not check_otp_rate_limit(phone_number):
            reason = "Per-phone OTP rate limit exceeded (5/hour)"
            log.status = SMSLog.Status.BLOCKED
            log.failure_reason = reason
            log.save(update_fields=["status", "failure_reason"])
            SMSLog.objects.create(
                phone_number=phone_number,
                message=message,
                category=category,
                status=SMSLog.Status.BLOCKED,
                failure_reason=reason,
                related_user=extra.get("user") if extra else None,
                related_organization=extra.get("org") if extra else None,
            )
            return False, "Rate limit exceeded. Please try again later."
        return True, ""

    @staticmethod
    def _truncate_message(message):
        truncated_message = message[:MAX_SMS_LENGTH]
        last_space = truncated_message.rfind(" ")
        if last_space > 0:
            truncated_message = truncated_message[:last_space]
        return truncated_message.strip()

    @staticmethod
    def _dispatch(phone_number, message, truncated):
        status = SMSLog.Status.SENT if not truncated else SMSLog.Status.TRUNCATED
        provider_response = None
        failure_reason = ""
        try:
            backend = MiMSMSBackend()
            provider_response = backend.send(phone_number, message)
        except Exception as e:
            status = SMSLog.Status.FAILED
            failure_reason = str(e)
            logger.exception("SMS send failed for %s", phone_number)
        return status, provider_response, failure_reason

    @staticmethod
    def format_otp_message(otp_code: str) -> str:
        """Format an OTP message within 160 chars."""
        return (
            f"Your Project Rokto verification code is: {otp_code}. "
            "It expires in 5 minutes."
        )

    @staticmethod
    def _shorten_urls_in_message(message: str) -> str:
        """Replace all URLs in a message with shortened versions."""

        def _replace_url(match):
            url = match.group(0)
            try:
                return shorten_url(url, category=ShortURL.Category.OTHER)
            except Exception:  # noqa: BLE001
                return url

        return URL_PATTERN.sub(_replace_url, message)
