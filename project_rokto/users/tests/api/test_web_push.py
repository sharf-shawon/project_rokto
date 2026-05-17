from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import cast

import pytest
from django.urls import reverse

from project_rokto.users.models import WebPushSubscription
from project_rokto.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from project_rokto.users.models import User

pytestmark = pytest.mark.django_db


def test_web_push_subscription_create(client):
    user = cast("User", UserFactory())
    client.force_login(user)

    url = reverse("api:web-push-subscriptions-list")
    data = {
        "endpoint": "https://fcm.googleapis.com/fcm/send/test-endpoint",
        "p256dh": "test-p256dh",
        "auth": "test-auth",
    }
    response = client.post(url, data)

    assert response.status_code == HTTPStatus.CREATED
    assert WebPushSubscription.objects.filter(
        user=user, endpoint=data["endpoint"]
    ).exists()


def test_web_push_subscription_unauthenticated(client):
    url = reverse("api:web-push-subscriptions-list")
    data = {
        "endpoint": "https://fcm.googleapis.com/fcm/send/test-endpoint",
        "p256dh": "test-p256dh",
        "auth": "test-auth",
    }
    response = client.post(url, data)

    assert response.status_code == HTTPStatus.FORBIDDEN
