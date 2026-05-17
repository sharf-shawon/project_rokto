from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import cast

import pytest
from django.test import RequestFactory

from project_rokto.organizations.admin import OrganizationMemberOrgAdmin
from project_rokto.organizations.admin import OrganizationOrgAdmin
from project_rokto.organizations.models import Organization
from project_rokto.organizations.models import OrganizationMember
from project_rokto.users.models import NIDVerification
from project_rokto.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from project_rokto.users.models import User

pytestmark = pytest.mark.django_db


def test_organization_org_admin_queryset():
    user = cast("User", UserFactory())
    org1 = Organization.objects.create(name="Org 1")
    Organization.objects.create(name="Org 2")
    org1.members.create(user=user, role=OrganizationMember.Role.ADMIN)

    admin = OrganizationOrgAdmin(Organization, None)
    rf = RequestFactory()

    # 1. Member user
    request = rf.get("/")
    request.user = user
    qs = admin.get_queryset(request)
    assert qs.count() == 1
    assert qs.first() == org1

    # 2. Superuser
    superuser = cast("User", UserFactory(is_superuser=True, is_staff=True))
    request.user = superuser
    qs = admin.get_queryset(request)
    expected_org_count = 2
    assert qs.count() == expected_org_count


def test_organization_org_admin_invite_manager_get():
    user = cast("User", UserFactory(is_staff=True, is_phone_verified=True))
    org = Organization.objects.create(name="Test Org")

    admin = OrganizationOrgAdmin(Organization, None)
    rf = RequestFactory()
    request = rf.get("/")
    request.user = user

    response = admin.invite_manager(request, Organization.objects.filter(id=org.id))
    assert response.status_code == HTTPStatus.OK
    # Check if the template-rendered content contains some expected text
    assert b"Invite Manager" in response.content


def test_organization_org_admin_invite_manager_post_success():
    admin_user = cast("User", UserFactory(is_staff=True))
    target_user = cast("User", UserFactory(username="target", is_phone_verified=True))
    NIDVerification.objects.create(
        user=target_user, status=NIDVerification.Status.VERIFIED
    )

    org = Organization.objects.create(name="Test Org")

    admin = OrganizationOrgAdmin(Organization, None)
    rf = RequestFactory()
    request = rf.post(
        "/",
        {
            "apply": "true",
            "username": "target",
            "role": OrganizationMember.Role.MANAGER,
        },
    )
    request.user = admin_user
    admin.message_user = lambda *args, **kwargs: None

    response = admin.invite_manager(request, Organization.objects.filter(id=org.id))
    assert response.status_code == HTTPStatus.FOUND
    assert OrganizationMember.objects.filter(
        user=target_user, organization=org
    ).exists()


def test_organization_org_admin_invite_manager_post_not_verified():
    admin_user = cast("User", UserFactory(is_staff=True))
    target_user = cast("User", UserFactory(username="target", is_phone_verified=False))

    org = Organization.objects.create(name="Test Org")

    admin = OrganizationOrgAdmin(Organization, None)
    rf = RequestFactory()
    request = rf.post("/", {"apply": "true", "username": "target"})
    request.user = admin_user
    admin.message_user = lambda *args, **kwargs: None

    response = admin.invite_manager(request, Organization.objects.filter(id=org.id))
    assert response.status_code == HTTPStatus.FOUND
    assert not OrganizationMember.objects.filter(
        user=target_user, organization=org
    ).exists()


def test_organization_org_admin_invite_manager_post_not_found():
    admin_user = cast("User", UserFactory(is_staff=True))
    org = Organization.objects.create(name="Test Org")

    admin = OrganizationOrgAdmin(Organization, None)
    rf = RequestFactory()
    request = rf.post("/", {"apply": "true", "username": "ghost"})
    request.user = admin_user
    admin.message_user = lambda *args, **kwargs: None

    response = admin.invite_manager(request, Organization.objects.filter(id=org.id))
    assert response.status_code == HTTPStatus.OK


def test_organization_member_org_admin_queryset():
    user = cast("User", UserFactory())
    org = Organization.objects.create(name="Org 1")
    org.members.create(user=user, role=OrganizationMember.Role.ADMIN)

    admin = OrganizationMemberOrgAdmin(OrganizationMember, None)
    rf = RequestFactory()
    request = rf.get("/")
    request.user = user

    qs = admin.get_queryset(request)
    assert qs.count() == 1


def test_organization_member_org_admin_queryset_superuser():
    superuser = cast("User", UserFactory(is_superuser=True, is_staff=True))
    org = Organization.objects.create(name="Super Org")
    org.members.create(
        user=cast("User", UserFactory()), role=OrganizationMember.Role.ADMIN
    )

    admin = OrganizationMemberOrgAdmin(OrganizationMember, None)
    rf = RequestFactory()
    request = rf.get("/")
    request.user = superuser

    qs = admin.get_queryset(request)
    assert qs.count() == 1


def test_organization_member_org_admin_permissions():
    admin_user = cast("User", UserFactory())
    manager_user = cast("User", UserFactory())
    org = Organization.objects.create(name="Test Org")
    member_admin = org.members.create(
        user=admin_user, role=OrganizationMember.Role.ADMIN
    )
    member_manager = org.members.create(
        user=manager_user, role=OrganizationMember.Role.MANAGER
    )

    admin = OrganizationMemberOrgAdmin(OrganizationMember, None)
    rf = RequestFactory()

    request = rf.get("/")
    request.user = admin_user
    assert admin.has_change_permission(request, member_manager) is True

    request.user = manager_user
    assert admin.has_change_permission(request, member_admin) is False

    superuser = cast("User", UserFactory(is_superuser=True, is_staff=True))
    request.user = superuser
    assert admin.has_change_permission(request, member_admin) is True
