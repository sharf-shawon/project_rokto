from http import HTTPStatus

import pytest
from django.urls import reverse

from project_rokto.donors.models import Donor
from project_rokto.organizations.models import Organization

pytestmark = pytest.mark.django_db


def test_guest_donor_links_to_new_user_on_signup(client):
    phone = "01712345678"
    org = Organization.objects.create(name="Red Crescent")

    # 1. Create a Guest Donor
    guest = Donor.objects.create(phone_number=phone)
    guest.organizations.add(org)

    # 2. Simulate verified phone in session
    session = client.session
    session["verified_phone_number"] = phone
    session.save()

    # 3. Complete signup
    url = reverse("users:signup_info")
    response = client.post(url, {"name": "Test User", "email": "test@example.com"})

    assert response.status_code == HTTPStatus.FOUND

    # 4. Verify linking
    guest.refresh_from_db()
    assert guest.user is not None
    assert guest.user.phone_number == phone
    assert guest.invite_status == Donor.InviteStatus.REGISTERED
    assert guest.organizations.filter(id=org.id).exists()


def test_signup_creates_fresh_donor_if_none_exists(client):
    phone = "01888888888"

    session = client.session
    session["verified_phone_number"] = phone
    session.save()

    url = reverse("users:signup_info")
    client.post(url, {"name": "New Donor", "email": "new@example.com"})

    assert Donor.objects.filter(phone_number=phone).exists()
    donor = Donor.objects.get(phone_number=phone)
    assert donor.user is not None
    assert donor.user.phone_number == phone
