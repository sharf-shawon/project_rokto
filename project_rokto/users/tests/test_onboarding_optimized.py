from http import HTTPStatus
from typing import cast

import pytest
from allauth.socialaccount.models import SocialLogin
from django.test import RequestFactory
from django.urls import reverse

from project_rokto.users.adapters import SocialAccountAdapter
from project_rokto.users.models import NIDVerification
from project_rokto.users.models import User
from project_rokto.users.tests.factories import NIDVerificationFactory
from project_rokto.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_middleware_superuser_exemption(admin_client):
    """Superusers should bypass verification middleware."""
    # Ensure admin has no NID or Phone verification
    admin_user = cast("User", User.objects.get(username="admin"))
    admin_user.is_phone_verified = False
    admin_user.save()

    url = reverse("home")
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_middleware_own_profile_exemption(client):
    """Users should be able to access their own profile without verification."""
    user = cast("User", UserFactory(is_phone_verified=False))
    client.force_login(user)

    url = reverse("users:detail", kwargs={"username": user.username})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_middleware_other_page_redirects(client):
    """Unverified users should still be redirected on other protected pages."""
    user = cast("User", UserFactory(is_phone_verified=False))
    client.force_login(user)

    url = reverse("blood_requests:dashboard")
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    # First redirect is to NID submission
    assert response.url == reverse("users:nid_submission")


def test_recovery_nudge_visibility(client):
    """Nudge should be visible for phone-only users without password."""
    user = cast("User", UserFactory(is_phone_verified=True, email=""))
    user.set_unusable_password()
    user.save()
    client.force_login(user)

    url = reverse("users:detail", kwargs={"username": user.username})
    response = client.get(url)
    content = response.content.decode()
    assert "Secure Your Account" in content
    assert reverse("account_email") in content
    assert reverse("account_set_password") in content


def test_recovery_nudge_hidden_when_secured(client):
    """Nudge should be hidden if email and password are set."""
    user = cast("User", UserFactory(is_phone_verified=True, email="test@example.com"))
    user.set_password("password123")
    user.save()
    client.force_login(user)

    url = reverse("users:detail", kwargs={"username": user.username})
    response = client.get(url)
    assert "Secure Your Account" not in response.content.decode()


def test_phone_signup_auto_verified(client):
    """Users from phone signup should be auto-verified."""
    session = client.session
    session["verified_phone_number"] = "01711112222"
    session.save()

    url = reverse("users:signup_info")
    client.post(url, {"name": "Test User", "email": ""})

    user = User.objects.get(phone_number="01711112222")
    assert user.is_phone_verified is True


def test_middleware_redirects_to_phone_when_not_verified(client):
    """User should be redirected to phone add if NID is verified but phone isn't."""
    user = cast("User", UserFactory(is_phone_verified=False))

    NIDVerificationFactory(user=user, status=NIDVerification.Status.VERIFIED)
    client.force_login(user)

    # Dashboard IS protected
    url = reverse("blood_requests:dashboard")
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("users:phone_add")


def test_notification_preference_view(client):
    """Test notification preference view coverage."""
    user = cast("User", UserFactory(is_phone_verified=True))

    NIDVerificationFactory(user=user, status=NIDVerification.Status.VERIFIED)
    client.force_login(user)

    url = reverse("users:notification_preferences")
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    response = client.post(url, {"email_enabled": True, "sms_enabled": True})
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("users:detail", kwargs={"username": user.username})


def test_social_account_adapter_populate_user():
    """Test SocialAccountAdapter populate_user coverage."""
    adapter = SocialAccountAdapter()
    rf = RequestFactory()
    request = rf.get("/")

    user = User()
    sociallogin = SocialLogin(user=user)

    # Test name population from 'name'
    data = {"name": "Social User", "first_name": "Social", "last_name": "User"}
    populated_user = adapter.populate_user(request, sociallogin, data)
    assert populated_user.name == "Social User"

    # Test name population from first/last name
    user2 = User()
    sociallogin2 = SocialLogin(user=user2)
    data2 = {"first_name": "First", "last_name": "Last"}
    populated_user2 = adapter.populate_user(request, sociallogin2, data2)
    assert populated_user2.name == "First Last"


def test_nid_submission_view_already_pending(client):
    """Test NIDSubmissionView when already pending (coverage)."""
    user = cast("User", UserFactory())

    NIDVerificationFactory(user=user, status=NIDVerification.Status.PENDING)
    client.force_login(user)

    url = reverse("users:nid_submission")
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    # Check for text in the alert-info block for pending status
    assert "Verification in Progress" in response.content.decode()

    # form_valid is safeguarded by dispatch which returns 200 when pending
    response = client.post(url, {})
    assert response.status_code == HTTPStatus.OK


def test_auth_pages_show_unified_links(client):
    """Phone and allauth pages should show unified auth links."""
    urls = [
        reverse("users:phone_login"),
        reverse("account_login"),
        reverse("account_signup"),
    ]
    for url in urls:
        response = client.get(url)
        content = response.content.decode()
        # Should show Phone option if not on phone login page
        if url != reverse("users:phone_login"):
            assert reverse("users:phone_login") in content

        # Should show Email options
        if url != reverse("account_login"):
            assert reverse("account_login") in content
        if url != reverse("account_signup"):
            assert reverse("account_signup") in content

        # Should show social providers (Google/Facebook)
        assert "Google" in content
        assert "Facebook" in content
