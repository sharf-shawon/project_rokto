from http import HTTPStatus
from typing import cast

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from project_rokto.users.backends import PhoneOTPBackend
from project_rokto.users.models import NIDVerification
from project_rokto.users.models import OTPRequest
from project_rokto.users.models import User
from project_rokto.users.tests.factories import OTPRequestFactory
from project_rokto.users.tests.factories import UserFactory

User_Model = get_user_model()
pytestmark = pytest.mark.django_db


def test_phone_login_view_get(client):
    url = reverse("users:phone_login")
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert "users/phone_login.html" in [t.name for t in response.templates]


def test_phone_login_page_shows_dual_purpose_and_links(client):
    """Phone login page shows dual sign in/up heading and auth method links."""
    url = reverse("users:phone_login")
    response = client.get(url)
    content = response.content.decode()

    # Check dual-purpose heading
    assert "Sign In / Sign Up with Phone" in content

    # Check links to other auth methods
    assert reverse("account_login") in content
    assert reverse("account_signup") in content


def test_phone_login_generates_otp(client):
    url = reverse("users:phone_login")
    response = client.post(url, {"phone_number": "01712345678"})
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("users:otp_verify")
    assert OTPRequest.objects.filter(phone_number="01712345678").exists()
    assert client.session["phone_number"] == "01712345678"


def test_otp_verify_view_get(client):
    url = reverse("users:otp_verify")
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_otp_verify_redirects_to_signup_info(client):
    OTPRequestFactory(phone_number="01712345678", otp_code="123456")
    session = client.session
    session["phone_number"] = "01712345678"
    session.save()

    url = reverse("users:otp_verify")
    response = client.post(url, {"otp_code": "123456"})
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("users:signup_info")
    assert client.session["verified_phone_number"] == "01712345678"
    assert not User_Model.objects.filter(phone_number="01712345678").exists()


def test_otp_verify_authenticates_existing_user(client):
    user = cast(
        "User",
        UserFactory(phone_number="01712345678", is_phone_verified=False),
    )
    OTPRequestFactory(phone_number="01712345678", otp_code="123456")
    session = client.session
    session["phone_number"] = "01712345678"
    session.save()

    url = reverse("users:otp_verify")
    response = client.post(url, {"otp_code": "123456"})
    assert response.status_code == HTTPStatus.FOUND
    user.refresh_from_db()
    assert user.is_phone_verified is True


def test_otp_verify_invalid_code(client):
    OTPRequestFactory(phone_number="01712345678", otp_code="123456")
    session = client.session
    session["phone_number"] = "01712345678"
    session.save()

    url = reverse("users:otp_verify")
    response = client.post(url, {"otp_code": "000000"})
    assert response.status_code == HTTPStatus.OK
    assert "Invalid or expired OTP." in response.content.decode()


def test_signup_info_view_with_email(client):
    """Test signup with email provided (backward compatibility)."""
    session = client.session
    session["verified_phone_number"] = "01712345678"
    session.save()

    url = reverse("users:signup_info")
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    response = client.post(
        url,
        {
            "name": "New User",
            "email": "newuser@example.com",
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    assert User_Model.objects.filter(phone_number="01712345678").exists()
    user = User_Model.objects.get(phone_number="01712345678")
    assert user.username == "01712345678"
    assert user.name == "New User"
    assert user.email == "newuser@example.com"
    assert user.is_phone_verified is True
    assert user.is_authenticated


def test_signup_info_view_without_email(client):
    """Test signup without email (email is optional)."""
    session = client.session
    session["verified_phone_number"] = "01812345678"
    session.save()

    url = reverse("users:signup_info")

    response = client.post(
        url,
        {
            "name": "Phone Only User",
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    assert User_Model.objects.filter(phone_number="01812345678").exists()
    user = User_Model.objects.get(phone_number="01812345678")
    assert user.username == "01812345678"
    assert user.name == "Phone Only User"
    assert user.email == ""  # No email provided
    assert user.is_phone_verified is True
    assert user.is_authenticated


def test_nid_submission_view(client):
    user = cast("User", UserFactory())
    client.force_login(user)
    url = reverse("users:nid_submission")

    # Mock images
    small_gif = (
        b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
        b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
        b"\x02\x4c\x01\x00\x3b"
    )
    front = SimpleUploadedFile("front.gif", small_gif, content_type="image/gif")
    back = SimpleUploadedFile("back.gif", small_gif, content_type="image/gif")

    response = client.post(url, {"front_image": front, "back_image": back})
    assert response.status_code == HTTPStatus.FOUND
    assert NIDVerification.objects.filter(user=user).exists()
    assert user.nid_verification.status == NIDVerification.Status.PENDING


def test_phone_add_verify_flow(client):
    user = cast("User", UserFactory(is_phone_verified=False))
    client.force_login(user)

    # 1. Add phone
    url = reverse("users:phone_add")
    response = client.post(url, {"phone_number": "01812345678"})
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("users:phone_verify_otp")
    assert client.session["pending_phone_number"] == "01812345678"

    # 2. Verify OTP with invalid code first
    url_otp = reverse("users:phone_verify_otp")
    response_invalid = client.post(url_otp, {"otp_code": "000000"})
    assert response_invalid.status_code == HTTPStatus.OK

    # 3. Verify OTP correctly
    OTPRequestFactory(phone_number="01812345678", otp_code="654321")
    response_otp = client.post(url_otp, {"otp_code": "654321"})
    assert response_otp.status_code == HTTPStatus.FOUND

    user.refresh_from_db()
    assert user.phone_number == "01812345678"
    assert user.is_phone_verified is True


def test_phone_otp_backend_edge_cases():
    backend = PhoneOTPBackend()

    # Missing phone or otp
    assert backend.authenticate(None, phone_number="01712345678") is None
    assert backend.authenticate(None, otp_code="123456") is None

    # Non-existent OTPRequest
    assert (
        backend.authenticate(None, phone_number="01712345678", otp_code="111111")
        is None
    )

    # get_user
    user = cast("User", UserFactory())
    assert backend.get_user(user.pk) == user
    assert backend.get_user(99999) is None
