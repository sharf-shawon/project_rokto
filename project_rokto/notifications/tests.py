"""Tests for the notifications app.

Covers: SMSLog, ShortURL, url_shortener, rate_limiter, UnifiedSMSService, backends.
"""

import datetime
from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.test import override_settings
from django.utils import timezone

from .backends import MiMSMSBackend
from .models import ShortURL
from .models import SMSLog
from .rate_limiter import OTP_RATE_KEY_PREFIX
from .rate_limiter import check_ip_rate_limit
from .rate_limiter import check_otp_rate_limit
from .rate_limiter import get_rate_limit_headers
from .services import UnifiedNotificationService
from .services import UnifiedSMSService
from .url_shortener import resolve_short_code
from .url_shortener import shorten_url

pytestmark = pytest.mark.django_db

EXCEED_LENGTH = 250
SHORT_MSG_LENGTH = 9
MIN_SHORT_CODE_LENGTH = 6
LONG_MESSAGE_LENGTH = 170
MAX_SMS_LENGTH = 160


# ─── SMSLog Model ─────────────────────────────────────────────────────────────


def test_smslog_creation():
    msg = "Test SMS"
    log = SMSLog.objects.create(
        phone_number="01712345678",
        message=msg,
        category=SMSLog.Category.OTP,
        status=SMSLog.Status.SENT,
    )
    assert log.message_length == len(msg)
    assert log.original_length == len(msg)
    assert "SENT" in str(log)
    assert "01712345678" in str(log)
    assert "OTP" in str(log)


def test_smslog_truncated_tracking():
    log = SMSLog.objects.create(
        phone_number="01712345678",
        message="Short msg",
        original_length=EXCEED_LENGTH,
        category=SMSLog.Category.EMERGENCY,
        status=SMSLog.Status.TRUNCATED,
    )
    assert log.original_length == EXCEED_LENGTH
    assert log.message_length == SHORT_MSG_LENGTH


# ─── ShortURL Model ───────────────────────────────────────────────────────────


def test_shorturl_expired():
    url = ShortURL.objects.create(
        original_url="https://example.com/expired",
        code="expired",
        expires_at=timezone.now() - datetime.timedelta(hours=1),
    )
    assert url.is_expired is True


def test_shorturl_not_expired():
    url = ShortURL.objects.create(
        original_url="https://example.com/active",
        code="active1",
        expires_at=timezone.now() + datetime.timedelta(days=7),
    )
    assert url.is_expired is False


def test_shorturl_no_expiry():
    url = ShortURL.objects.create(
        original_url="https://example.com/no-expiry",
        code="noexpir",
    )
    assert url.is_expired is False


# ─── URL Shortener ────────────────────────────────────────────────────────────


@override_settings(SHORT_URL_DOMAIN="https://rkto.gg", SHORT_URL_SALT="test_salt")
def test_shorten_url_creates_code():
    short = shorten_url(
        "https://example.com/long-url", category=ShortURL.Category.OTHER
    )
    assert short.startswith("https://rkto.gg/")
    assert short.endswith("/")
    code = short.split("/")[-2]
    assert len(code) >= MIN_SHORT_CODE_LENGTH


@override_settings(SHORT_URL_DOMAIN="https://rkto.gg", SHORT_URL_SALT="test_salt")
def test_shorten_url_deduplication():
    url = "https://example.com/unique-url"
    short1 = shorten_url(url)
    short2 = shorten_url(url)
    assert short1 == short2
    assert ShortURL.objects.count() == 1


@override_settings(SHORT_URL_DOMAIN="https://rkto.gg", SHORT_URL_SALT="test_salt")
def test_resolve_short_code():
    short = shorten_url("https://example.com/resolve-me")
    code = short.split("/")[-2]
    resolved = resolve_short_code(code)
    assert resolved == "https://example.com/resolve-me"


def test_resolve_short_code_unknown():
    assert resolve_short_code("unknown") is None


@override_settings(SHORT_URL_SALT="test_salt")
def test_resolve_short_code_expired():
    url = ShortURL.objects.create(
        original_url="https://example.com/old",
        code="oldcode",
        expires_at=timezone.now() - datetime.timedelta(days=1),
    )
    assert resolve_short_code(url.code) is None


# ─── Rate Limiter ─────────────────────────────────────────────────────────────


def test_otp_rate_limit_allows_first_request():
    cache.clear()
    assert check_otp_rate_limit("01700000001") is True


def test_otp_rate_limit_blocks_after_limit():
    cache.clear()
    phone = "01700000002"

    for _ in range(5):
        assert check_otp_rate_limit(phone) is True

    assert check_otp_rate_limit(phone) is False


def test_ip_rate_limit_allows_first_request():
    cache.clear()
    assert check_ip_rate_limit("192.168.1.1") is True


def test_ip_rate_limit_blocks_second_request():
    cache.clear()
    ip = "192.168.1.2"
    assert check_ip_rate_limit(ip) is True
    assert check_ip_rate_limit(ip) is False


def test_rate_limit_headers():
    cache.clear()
    headers = get_rate_limit_headers(OTP_RATE_KEY_PREFIX, "01700000003", 5)
    assert "X-RateLimit-Limit" in headers
    assert "X-RateLimit-Remaining" in headers
    assert "X-RateLimit-Reset" in headers
    assert headers["X-RateLimit-Limit"] == "5"


# ─── UnifiedSMSService ────────────────────────────────────────────────────────


@patch("project_rokto.notifications.backends.MiMSMSBackend.send")
def test_unified_sms_service_send_success(mock_send):
    mock_send.return_value = {"status": "sent", "trxn_id": "test123"}

    success, msg = UnifiedSMSService.send(
        phone_number="01712345678",
        message="Test message",
        category=SMSLog.Category.OTHER,
    )

    assert success is True
    assert "sent successfully" in msg.lower()
    assert SMSLog.objects.filter(
        phone_number="01712345678", status=SMSLog.Status.SENT
    ).exists()


@patch("project_rokto.notifications.backends.MiMSMSBackend.send")
def test_unified_sms_service_otp_rate_limit(mock_send):
    mock_send.return_value = {"status": "sent", "trxn_id": "test123"}
    cache.clear()

    phone = "01700000010"

    for _ in range(5):
        success, _ = UnifiedSMSService.send(
            phone_number=phone,
            message="Your code is: 123456",
            category=SMSLog.Category.OTP,
        )
        assert success is True

    success, msg = UnifiedSMSService.send(
        phone_number=phone,
        message="Your code is: 654321",
        category=SMSLog.Category.OTP,
    )
    assert success is False
    assert "Rate limit exceeded" in msg
    assert SMSLog.objects.filter(
        phone_number=phone, status=SMSLog.Status.BLOCKED
    ).exists()


@patch("project_rokto.notifications.backends.MiMSMSBackend.send")
def test_unified_sms_service_truncation(mock_send):
    mock_send.return_value = {"status": "sent", "trxn_id": "test123"}

    long_message = "A" * LONG_MESSAGE_LENGTH
    success, _msg = UnifiedSMSService.send(
        phone_number="01712345678",
        message=long_message,
        category=SMSLog.Category.OTHER,
    )

    assert success is True
    log = SMSLog.objects.filter(phone_number="01712345678").latest("created_at")
    assert log.message_length <= MAX_SMS_LENGTH
    assert log.original_length == LONG_MESSAGE_LENGTH
    assert log.status == SMSLog.Status.TRUNCATED


@patch("project_rokto.notifications.backends.MiMSMSBackend.send")
def test_unified_sms_service_url_shortening(mock_send):
    mock_send.return_value = {"status": "sent", "trxn_id": "test123"}

    success, _ = UnifiedSMSService.send(
        phone_number="01712345678",
        message="Check this link: https://example.com/very/long/path?token=abc123",
        category=SMSLog.Category.OTHER,
    )
    assert success is True


@patch("project_rokto.notifications.backends.MiMSMSBackend.send")
def test_unified_sms_service_send_failure(mock_send):
    mock_send.side_effect = Exception("Provider timeout")

    success, _msg = UnifiedSMSService.send(
        phone_number="01712345678",
        message="Test failure",
        category=SMSLog.Category.OTHER,
    )

    assert success is False
    log = SMSLog.objects.filter(phone_number="01712345678").latest("created_at")
    assert log.status == SMSLog.Status.FAILED


@patch("project_rokto.notifications.backends.MiMSMSBackend.send")
def test_unified_notification_service_send_otp_convenience(mock_send):
    mock_send.return_value = {"status": "sent", "trxn_id": "test123"}
    cache.clear()

    success, _msg = UnifiedNotificationService.send_otp(
        phone_number="01712345678",
        otp_code="987654",
    )

    assert success is True
    log = SMSLog.objects.filter(phone_number="01712345678").latest("created_at")
    assert log.category == SMSLog.Category.OTP
    assert "987654" in log.message


# ─── MiMSMSBackend ─────────────────────────────────────────────────────────────


@patch("django_mimsms.client.MiMSMSClient.send_sms")
def test_mimsms_backend_success(mock_send_sms):
    mock_response = type(
        "MockResponse",
        (),
        {"trxn_id": "trxn123", "model_dump": lambda self: {"id": "1"}},
    )()
    mock_send_sms.return_value = mock_response

    backend = MiMSMSBackend()
    result = backend.send("01712345678", "Test message")

    assert result["status"] == "sent"
    assert result["trxn_id"] == "trxn123"


@patch("django_mimsms.client.MiMSMSClient.send_sms")
def test_mimsms_backend_adds_country_code(mock_send_sms):
    mock_response = type(
        "MockResponse",
        (),
        {"trxn_id": "", "model_dump": lambda self: {"id": "1"}},
    )()
    mock_send_sms.return_value = mock_response

    backend = MiMSMSBackend()
    backend.send("01712345678", "Test")

    call_args = mock_send_sms.call_args[0]
    assert call_args[0] == "8801712345678"
