import io
from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import cast

import pytest
from django.urls import reverse

from project_rokto.donors.models import Donor
from project_rokto.organizations.models import Organization
from project_rokto.organizations.models import OrganizationMember
from project_rokto.organizations.services import DonorImportService
from project_rokto.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from project_rokto.users.models import User

pytestmark = pytest.mark.django_db


def test_organization_api_get_queryset(client):
    user = cast("User", UserFactory())
    org1 = Organization.objects.create(name="Org 1")
    Organization.objects.create(name="Org 2")
    org1.members.create(user=user, role=OrganizationMember.Role.ADMIN)

    client.force_login(user)
    url = reverse("api:organizations-list")
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    # Should only see org1
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Org 1"


def test_organization_api_upload_donors_permissions(client):
    user_no_perm = cast("User", UserFactory())
    user_manager = cast("User", UserFactory())
    org = Organization.objects.create(name="Test Org")
    org.members.create(user=user_manager, role=OrganizationMember.Role.MANAGER)

    url = reverse("api:organizations-upload-donors", kwargs={"pk": org.pk})

    # 1. Unauthenticated
    response = client.post(url)
    assert response.status_code == HTTPStatus.FORBIDDEN

    # 2. Authenticated but no membership
    client.force_login(user_no_perm)
    response = client.post(url)
    # DRF get_object will fail if not in queryset
    assert response.status_code == HTTPStatus.NOT_FOUND

    # 4. Correct permissions but no file
    client.force_login(user_manager)
    response = client.post(url)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.data["error"] == "No file uploaded (key 'file' expected)"


def test_organization_api_upload_donors_success(client):
    user = cast("User", UserFactory())
    org = Organization.objects.create(name="Test Org")
    org.members.create(user=user, role=OrganizationMember.Role.ADMIN)

    url = reverse("api:organizations-upload-donors", kwargs={"pk": org.pk})
    client.force_login(user)

    csv_content = "phone_number,name,blood_group\n01712345678,New Donor,A+"
    csv_file = io.BytesIO(csv_content.encode())
    csv_file.name = "donors.csv"

    response = client.post(url, {"file": csv_file}, format="multipart")

    assert response.status_code == HTTPStatus.OK
    assert response.data["created"] == 1
    assert Donor.objects.filter(phone_number="01712345678").exists()


def test_donor_import_service_edge_cases():
    org = Organization.objects.create(name="Edge Org")

    # 1. Skipped (missing phone)
    csv_content = "phone_number,name,blood_group\n,Ghost Donor,A+"
    results = DonorImportService.import_from_csv(org, csv_content.encode())
    assert results["skipped"] == 1

    # 2. Error (invalid blood group choice)
    csv_content = "phone_number,name,blood_group\n01700000000,Bad Donor,INVALID_BG"
    results = DonorImportService.import_from_csv(org, csv_content.encode())
    assert len(results["errors"]) == 1
    assert "Error processing" in results["errors"][0]
