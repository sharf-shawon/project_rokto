import logging
import re

from django.conf import settings

from .backends import MiMSMSBackend
from .models import ShortURL
from .models import SMSLog
from .rate_limiter import check_otp_rate_limit
from .url_shortener import shorten_url

logger = logging.getLogger(__name__)

MAX_SMS_LENGTH = 160
SMS_ALERT_THRESHOLD = getattr(settings, "SMS_ALERT_THRESHOLD", 140)
URL_PATTERN = re.compile(r"https?://[^\s]+")


class UnifiedSMSService:
    """Centralized SMS sending service.

    All SMS flows through this service, which handles:
    1. URL shortening
    2. 160-char validation/truncation
    3. Rate limiting (per-phone for OTP)
    4. Provider dispatch
    5. Centralized audit logging (SMSLog)
    """

    @staticmethod
    def send(
        phone_number: str,
        message: str,
        category: str = SMSLog.Category.OTHER,
        related_user=None,
        related_organization=None,
    ) -> tuple[bool, str]:
        """Send an SMS through the configured provider."""
        # 1. Shorten URLs
        if "http" in message:
            message = UnifiedSMSService._shorten_urls_in_message(message)

        # 2. Per-phone OTP rate limit
        if category == SMSLog.Category.OTP:
            if not check_otp_rate_limit(phone_number):
                SMSLog.objects.create(
                    phone_number=phone_number,
                    message=message,
                    category=category,
                    status=SMSLog.Status.BLOCKED,
                    failure_reason="Per-phone OTP rate limit exceeded (5/hour)",
                    related_user=related_user,
                    related_organization=related_organization,
                )
                return False, "Rate limit exceeded. Please try again later."

        # 3. 160-char limit enforcement
        truncated = False
        original_length = len(message)
        if original_length > MAX_SMS_LENGTH:
            truncated = True
            truncated_message = message[:MAX_SMS_LENGTH]
            last_space = truncated_message.rfind(" ")
            if last_space > 0:
                truncated_message = truncated_message[:last_space]
            message = truncated_message.strip()
        elif original_length > SMS_ALERT_THRESHOLD:
            logger.info("SMS approaching limit: %d chars", original_length)

        # 4. Send via provider
        status = SMSLog.Status.SENT if not truncated else SMSLog.Status.TRUNCATED
        provider_response = None
        failure_reason = ""

        try:
            backend = MiMSMSBackend()
            result = backend.send(phone_number, message)
            provider_response = result
        except Exception as e:
            status = SMSLog.Status.FAILED
            failure_reason = str(e)
            logger.exception("SMS send failed for %s", phone_number)

        # 5. Log to SMSLog
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

        if status in (SMSLog.Status.SENT, SMSLog.Status.TRUNCATED):
            return True, "SMS sent successfully."
        return False, failure_reason or "SMS sending failed."

    @staticmethod
    def send_otp(
        phone_number: str,
        otp_code: str,
        related_user=None,
        related_organization=None,
    ) -> tuple[bool, str]:
        """Convenience method for sending OTP SMS."""
        message = UnifiedSMSService._format_otp_message(otp_code)
        return UnifiedSMSService.send(
            phone_number=phone_number,
            message=message,
            category=SMSLog.Category.OTP,
            related_user=related_user,
            related_organization=related_organization,
        )

    @staticmethod
    def _format_otp_message(otp_code: str) -> str:
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

        return URL_PATTERN.sub(_replace_url, message)
