from http import HTTPStatus

import pytest
from django.urls import reverse

from project_rokto.users.models import NIDVerification


def test_api_docs_accessible_by_admin(admin_client, admin_user):
    admin_user.is_phone_verified = True
    admin_user.save()
    NIDVerification.objects.create(
        user=admin_user,
        status=NIDVerification.Status.VERIFIED,
    )

    url = reverse("api-docs")
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_api_docs_not_accessible_by_anonymous_users(client):
    url = reverse("api-docs")
    response = client.get(url)
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_api_schema_generated_successfully(admin_client, admin_user):
    admin_user.is_phone_verified = True
    admin_user.save()
    NIDVerification.objects.create(
        user=admin_user,
        status=NIDVerification.Status.VERIFIED,
    )

    url = reverse("api-schema")
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK
