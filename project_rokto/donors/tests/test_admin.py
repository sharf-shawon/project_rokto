from typing import TYPE_CHECKING
from typing import cast

import pytest
from django.test import RequestFactory

from project_rokto.donors.admin import DonorOrgAdmin
from project_rokto.donors.models import Donor
from project_rokto.donors.models import OrganizationDonorData
from project_rokto.organizations.models import Organization
from project_rokto.organizations.models import OrganizationMember
from project_rokto.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from project_rokto.users.models import User

pytestmark = pytest.mark.django_db


def test_donor_org_admin_queryset():
    # Clear existing to have exact counts
    Donor.objects.all().delete()

    user = cast("User", UserFactory())
    org = Organization.objects.create(name="Org")
    org.members.create(user=user, role=OrganizationMember.Role.ADMIN)

    donor1 = Donor.objects.create(phone_number="01700000001")
    OrganizationDonorData.objects.create(organization=org, donor=donor1)

    Donor.objects.create(phone_number="01700000002")  # Not linked

    admin = DonorOrgAdmin(Donor, None)
    rf = RequestFactory()
    request = rf.get("/")
    request.user = user

    qs = admin.get_queryset(request)
    assert qs.count() == 1
    assert qs.first() == donor1

    # Superuser
    superuser = cast("User", UserFactory(is_superuser=True, is_staff=True))
    request.user = superuser
    # donor1 + donor2 + superuser_donor + user_donor = 4
    expected_min_donors = 2
    assert admin.get_queryset(request).count() >= expected_min_donors


def test_donor_org_admin_save_model():
    user = cast("User", UserFactory())
    org = Organization.objects.create(name="Org")
    org.members.create(user=user, role=OrganizationMember.Role.ADMIN)

    admin = DonorOrgAdmin(Donor, None)
    rf = RequestFactory()
    request = rf.get("/")
    request.user = user

    donor = Donor(phone_number="01700000003")
    admin.save_model(request, donor, form=None, change=False)

    assert Donor.objects.filter(phone_number="01700000003").exists()
    assert OrganizationDonorData.objects.filter(organization=org, donor=donor).exists()
