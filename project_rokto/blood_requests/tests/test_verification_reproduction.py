from http import HTTPStatus
from typing import cast

import pytest
from django.urls import reverse

from project_rokto.users.models import NIDVerification
from project_rokto.users.models import User
from project_rokto.users.tests.factories import NIDVerificationFactory
from project_rokto.users.tests.factories import UserFactory


@pytest.mark.django_db
def test_verified_user_can_send_request(client):
    # 1. Create a fully verified user
    user = cast("User", UserFactory(is_phone_verified=True))
    NIDVerificationFactory(user=user, status=NIDVerification.Status.VERIFIED)

    assert user.is_phone_verified is True
    assert user.nid_verification.status == NIDVerification.Status.VERIFIED
    assert user.is_verified is True

    client.force_login(user)

    # 2. Try to send a blood request
    donor = cast("User", UserFactory())
    url = reverse("api:requests-list")
    payload = {
        "reason": "Emergency surgery",
        "bags_needed": 1,
        "donation_date": "2026-06-01",
        "hospital": "City Hospital",
        "donor_ids": [donor.id],
    }

    response = client.post(url, payload, content_type="application/json")

    # If this fails with 400 and the "verify" message, we reproduced it.
    assert response.status_code == HTTPStatus.CREATED, f"Response: {response.data}"


@pytest.mark.django_db
def test_unverified_user_gets_correct_error(client):
    # User with only phone verified
    user = cast("User", UserFactory(is_phone_verified=True))
    # NID is PENDING by default if we don't create it or we create it as pending
    NIDVerificationFactory(user=user, status=NIDVerification.Status.PENDING)

    client.force_login(user)

    donor = cast("User", UserFactory())
    url = reverse("api:requests-list")
    payload = {
        "reason": "Test",
        "bags_needed": 1,
        "donation_date": "2026-06-01",
        "hospital": "Test Hospital",
        "donor_ids": [donor.id],
    }

    response = client.post(url, payload, content_type="application/json")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "verify" in str(response.json())
