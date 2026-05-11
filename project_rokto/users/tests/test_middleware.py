from http import HTTPStatus

import pytest
from django.urls import reverse

from project_rokto.users.models import NIDVerification
from project_rokto.users.tests.factories import NIDVerificationFactory
from project_rokto.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_middleware_redirects_unverified_user(client):
    user = UserFactory()
    client.force_login(user)

    url = reverse("users:detail", kwargs={"username": user.username})
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("users:nid_submission")


def test_middleware_redirects_to_phone_after_nid_verified(client):
    user = UserFactory(is_phone_verified=False)
    NIDVerificationFactory(user=user, status=NIDVerification.Status.VERIFIED)
    client.force_login(user)

    url = reverse("users:detail", kwargs={"username": user.username})
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("users:phone_add")


def test_middleware_allows_verified_user(client):
    user = UserFactory(is_phone_verified=True)
    NIDVerificationFactory(user=user, status=NIDVerification.Status.VERIFIED)
    client.force_login(user)

    url = reverse("users:detail", kwargs={"username": user.username})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_middleware_exempts_static_and_media(client):
    user = UserFactory()
    client.force_login(user)

    # Static and media usually served by webserver, but middleware might see them in dev
    response = client.get("/static/css/project.css")
    # Even if file doesn't exist, it shouldn't redirect if it's in exempt_urls
    assert response.status_code != HTTPStatus.FOUND or not response.url.endswith(
        reverse("users:nid_submission"),
    )


def test_middleware_exempts_admin(client):
    user = UserFactory(is_staff=True, is_superuser=True)
    client.force_login(user)

    response = client.get("/admin/")
    # Admin should be accessible even if user is not verified
    # (to allow admin to verify others)
    assert response.status_code == HTTPStatus.OK
