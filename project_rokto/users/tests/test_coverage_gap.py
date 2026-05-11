import datetime
from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import cast

import pytest
from django.urls import reverse
from django.utils import timezone

from project_rokto.users.backends import PhoneOTPBackend
from project_rokto.users.forms import PhoneAddForm
from project_rokto.users.forms import UserUpdateForm
from project_rokto.users.models import NIDVerification
from project_rokto.users.models import OTPRequest
from project_rokto.users.models import User
from project_rokto.users.tests.factories import LocationFactory
from project_rokto.users.tests.factories import NIDVerificationFactory
from project_rokto.users.tests.factories import UserFactory
from project_rokto.users.utils import obfuscate_name
from project_rokto.users.utils import obfuscate_phone_number

if TYPE_CHECKING:
    from project_rokto.locations.models import Location

pytestmark = pytest.mark.django_db


def create_verified_user(**kwargs):
    user = cast("User", UserFactory(is_phone_verified=True, **kwargs))
    NIDVerificationFactory(user=user, status=NIDVerification.Status.VERIFIED)
    return user


def test_obfuscate_utils_edge_cases():
    # utils.py
    assert obfuscate_phone_number("") == ""
    assert obfuscate_phone_number("123") == "123"  # too short

    assert obfuscate_name("") == "Donor"
    assert obfuscate_name("SingleName") == "SingleName"


def test_phone_otp_backend_invalid_cases():
    backend = PhoneOTPBackend()

    # Missing params
    assert backend.authenticate(None) is None
    assert backend.authenticate(None, phone_number="01712345678") is None

    # Non-existent OTP
    assert (
        backend.authenticate(None, phone_number="01712345678", otp_code="123456")
        is None
    )

    # Expired OTP
    otp = OTPRequest.objects.create(
        phone_number="01712345678",
        otp_code="123456",
        expires_at=timezone.now() - datetime.timedelta(minutes=1),
    )
    assert (
        backend.authenticate(None, phone_number="01712345678", otp_code="123456")
        is None
    )

    # Existing user, not phone verified (Hits lines 38-39 in backends.py)
    user_existing = cast(
        "User", UserFactory(phone_number="01712345678", is_phone_verified=False)
    )
    otp.expires_at = timezone.now() + datetime.timedelta(minutes=5)
    otp.save()
    authenticated_user = backend.authenticate(
        None,
        phone_number="01712345678",
        otp_code="123456",
    )
    assert authenticated_user == user_existing
    assert authenticated_user is not None
    assert authenticated_user.is_phone_verified is True

    # Test get_user
    assert backend.get_user(authenticated_user.id) == authenticated_user
    assert backend.get_user(9999) is None


def test_user_update_form_init_and_clean():
    user = cast(
        "User", UserFactory(allergies=["Peanuts"], health_conditions=["Asthma"])
    )
    loc1 = cast("Location", LocationFactory())
    loc2 = cast("Location", LocationFactory())

    # Init with instance
    form = UserUpdateForm(instance=user)
    assert form.initial["allergies"] == "Peanuts"
    assert form.initial["health_conditions"] == "Asthma"

    # Bound form with new location
    data = {
        "name": "New Name",
        "blood_group": "A+",
        "preferred_locations": [loc1.id, loc2.id],
        "allergies": "Milk, Eggs ",
        "health_conditions": " None",
    }
    form = UserUpdateForm(data=data, instance=user)
    assert form.is_valid()
    assert form.cleaned_data["allergies"] == ["Milk", "Eggs"]
    assert form.cleaned_data["health_conditions"] == ["None"]

    # Fallback for non-QueryDict preferred_locations
    UserUpdateForm(data={"preferred_locations": loc1.id})


def test_phone_add_form_duplicate():
    cast("User", UserFactory(phone_number="01711111111"))
    user2 = cast("User", UserFactory(phone_number="01722222222"))

    form = PhoneAddForm(data={"phone_number": "01711111111"}, user=user2)
    assert not form.is_valid()
    assert "already in use" in form.errors["phone_number"][0]


def test_signup_info_view_redirect(client):
    # No verified_phone_number in session
    response = client.get(reverse("users:signup_info"))
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("users:phone_login")


def test_signup_info_view_valid_post(client):
    # Valid verified_phone_number in session (Hits line 214 in users/views.py)
    session = client.session
    session["verified_phone_number"] = "01712345678"
    session.save()

    response = client.post(
        reverse("users:signup_info"),
        {"name": "New User", "email": "new@example.com"},
    )
    assert response.status_code == HTTPStatus.FOUND
    user = User.objects.get(phone_number="01712345678")
    assert user.name == "New User"


def test_nid_submission_view_verified_redirect(client):
    user = create_verified_user()
    client.force_login(user)

    response = client.get(reverse("users:nid_submission"))
    assert response.status_code == HTTPStatus.OK
    assert "nid" in response.context


def test_nid_submission_view_pending_redirect(client):
    user = cast("User", UserFactory())
    NIDVerification.objects.create(user=user, status=NIDVerification.Status.PENDING)
    client.force_login(user)

    response = client.get(reverse("users:nid_submission"))
    assert response.status_code == HTTPStatus.OK


def test_nid_submission_view_max_attempts(client):
    user = cast(
        "User", UserFactory(verification_attempts=User.MAX_VERIFICATION_ATTEMPTS)
    )
    client.force_login(user)

    response = client.get(reverse("users:nid_submission"))
    assert response.status_code == HTTPStatus.OK
    assert response.context["attempts_left"] == 0


def test_nid_submission_view_logged_out_dispatch(client):
    # Hits line 244 in users/views.py
    response = client.get(reverse("users:nid_submission"))
    assert response.status_code == HTTPStatus.FOUND


def test_phone_manage_view_same_number(client):
    user = create_verified_user(phone_number="01712345678")
    client.force_login(user)

    response = client.post(
        reverse("users:phone_manage"),
        {"phone_number": "01712345678"},
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("users:phone_manage")


def test_user_update_view_autocomplete_context(client):
    UserFactory(allergies=["Dust"], health_conditions=["Diabetes"])
    user = create_verified_user()
    client.force_login(user)

    response = client.get(reverse("users:update"))
    assert response.status_code == HTTPStatus.OK
    assert "Dust" in response.context["existing_allergies"]
    assert "Diabetes" in response.context["existing_conditions"]
