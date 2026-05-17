import pytest
from django.contrib.gis.geos import Point

from project_rokto.donors.models import Donor
from project_rokto.locations.models import Location
from project_rokto.users.forms import UserUpdateForm
from project_rokto.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_donor_profile_form_save():
    user = UserFactory()
    location = Location.objects.create(
        post_code="1234",
        area_name="Area",
        station="Station",
        district="District",
        division="Division",
        point=Point(0, 0),
    )

    data = {
        "name": "Updated Name",
        "blood_group": "A+",
        "date_of_birth": "1990-01-01",
        "last_donation_date": "2023-01-01",
        "is_available_to_donate": True,
        "allergies": "Peanuts, Dust",
        "health_conditions": "None",
        "preferred_locations": [location.pk],
    }

    form = UserUpdateForm(data=data, instance=user)
    assert form.is_valid(), form.errors

    saved_user = form.save()
    assert saved_user.name == "Updated Name"

    donor = Donor.objects.get(user=saved_user)
    assert donor.blood_group == "A+"
    assert donor.allergies == ["Peanuts", "Dust"]
    assert donor.preferred_locations.count() == 1


def test_donor_profile_form_save_no_commit():
    user = UserFactory()
    data = {
        "name": "Updated Name",
        "blood_group": "A+",
    }
    form = UserUpdateForm(data=data, instance=user)
    assert form.is_valid()

    # Save with commit=False
    form.save(commit=False)
    # Check that donor was NOT saved to DB if commit=False
    assert not Donor.objects.filter(blood_group="A+").exists()
