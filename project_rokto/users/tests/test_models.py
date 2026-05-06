import datetime
from typing import cast

import pytest
from django.utils import timezone

from project_rokto.users.models import NIDVerification
from project_rokto.users.models import OTPRequest
from project_rokto.users.models import User
from project_rokto.users.tests.factories import NIDVerificationFactory
from project_rokto.users.tests.factories import OTPRequestFactory
from project_rokto.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_user_get_absolute_url(user: User):
    assert user.get_absolute_url() == f"/users/{user.username}/"


def test_user_is_verified_property():
    user = cast("User", UserFactory(is_phone_verified=True))
    assert user.is_verified is False

    NIDVerificationFactory(user=user, status=NIDVerification.Status.VERIFIED)
    assert user.is_verified is True

    user.is_phone_verified = False
    assert user.is_verified is False


def test_otp_request_is_valid():
    otp = cast(
        "OTPRequest",
        OTPRequestFactory(
            is_used=False,
            expires_at=timezone.now() + datetime.timedelta(minutes=5),
        ),
    )
    assert otp.is_valid() is True

    otp.is_used = True
    assert otp.is_valid() is False

    otp2 = cast(
        "OTPRequest",
        OTPRequestFactory(
            is_used=False,
            expires_at=timezone.now() - datetime.timedelta(minutes=5),
        ),
    )
    assert otp2.is_valid() is False


def test_nid_verification_str():
    nid = cast("NIDVerification", NIDVerificationFactory())
    assert str(nid) == f"NID Verification for {nid.user.username} ({nid.status})"


def test_otp_request_str():
    otp = cast("OTPRequest", OTPRequestFactory(phone_number="01712345678"))
    assert "OTP for 01712345678" in str(otp)
