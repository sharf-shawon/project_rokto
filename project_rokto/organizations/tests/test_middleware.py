from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import cast

import pytest
from django.urls import reverse

from project_rokto.organizations.models import Organization
from project_rokto.organizations.models import OrganizationMember
from project_rokto.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from project_rokto.users.models import User

pytestmark = pytest.mark.django_db


def test_org_manager_mfa_middleware_enforcement(client):
    user = cast("User", UserFactory())
    org = Organization.objects.create(name="Test Org")
    org.members.create(user=user, role=OrganizationMember.Role.MANAGER)

    # User is org manager but has no MFA
    client.force_login(user)

    url = "/org-admin/some-page/"
    response = client.get(url)

    # Should redirect to mfa_index
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("mfa_index")


def test_org_manager_mfa_middleware_exempt(client):
    user = cast("User", UserFactory())
    org = Organization.objects.create(name="Test Org")
    org.members.create(user=user, role=OrganizationMember.Role.MANAGER)

    client.force_login(user)

    # Logout is exempt
    response = client.get(reverse("account_logout"))
    assert response.status_code != HTTPStatus.FOUND or response.url != reverse(
        "mfa_index"
    )
