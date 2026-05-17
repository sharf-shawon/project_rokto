from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import cast

import pytest
from django.urls import reverse

from project_rokto.organizations.models import Organization
from project_rokto.organizations.models import OrganizationMember
from project_rokto.users.models import NIDVerification
from project_rokto.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from project_rokto.users.models import User

pytestmark = pytest.mark.django_db


def test_organization_detail_view(client):
    org = Organization.objects.create(name="Test Org")
    url = reverse("organizations:detail", kwargs={"slug": org.slug})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert response.context["donor_count"] == 0


def test_create_organization_view_unauthenticated(client):
    url = reverse("organizations:create")
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert "login" in response.url


def test_create_organization_view_not_verified(client):
    user = cast("User", UserFactory(is_phone_verified=False))
    client.force_login(user)
    url = reverse("organizations:create")
    response = client.get(url)
    # Redirected by VerificationMiddleware to NID submission
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("users:nid_submission")


def test_create_organization_view_success(client):
    user = cast("User", UserFactory(is_phone_verified=True))
    NIDVerification.objects.create(user=user, status=NIDVerification.Status.VERIFIED)
    client.force_login(user)

    url = reverse("organizations:create")
    response = client.post(
        url, {"name": "New Org", "basic_info": "Info", "contact_information": "Contact"}
    )

    assert response.status_code == HTTPStatus.FOUND
    assert Organization.objects.filter(name="New Org").exists()
    org = Organization.objects.get(name="New Org")
    assert OrganizationMember.objects.filter(
        organization=org, user=user, role=OrganizationMember.Role.ADMIN
    ).exists()


def test_organization_list_view(client):
    Organization.objects.create(name="Org 1")
    url = reverse("organizations:list")
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert len(response.context["organizations"]) == 1
