import datetime
from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import cast

import pytest
from django.contrib.gis.geos import Point
from django.urls import reverse
from django.utils import timezone

from project_rokto.users.models import NIDVerification
from project_rokto.users.tests.factories import LocationFactory
from project_rokto.users.tests.factories import NIDVerificationFactory
from project_rokto.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from project_rokto.locations.models import Location
    from project_rokto.users.models import User


@pytest.mark.django_db
def test_donor_search_compatibility_filtering(client):
    """
    Test that search only returns compatible blood groups.
    """
    seeker_bg = "A+"
    compatible_groups = ["A+", "A-", "O+", "O-"]
    incompatible_groups = ["B+", "B-", "AB+", "AB-"]

    target_loc = cast("Location", LocationFactory(point=Point(90.0, 23.0)))

    # Create compatible available donors
    for bg in compatible_groups:
        user = cast(
            "User",
            UserFactory(
                blood_group=bg,
                is_available_to_donate=True,
                is_phone_verified=True,
            ),
        )
        NIDVerificationFactory(user=user, status=NIDVerification.Status.VERIFIED)
        user.donor_profile.preferred_locations.add(target_loc)

    # Create incompatible available donors
    for bg in incompatible_groups:
        user = cast(
            "User",
            UserFactory(
                blood_group=bg,
                is_available_to_donate=True,
                is_phone_verified=True,
            ),
        )
        NIDVerificationFactory(user=user, status=NIDVerification.Status.VERIFIED)
        user.donor_profile.preferred_locations.add(target_loc)

    url = reverse("api:donors-list")
    response = client.get(url, {"blood_group": seeker_bg, "location_id": target_loc.id})

    assert response.status_code == HTTPStatus.OK
    results = response.json()

    # Check that all returned donors are compatible
    for donor in results:
        assert donor["blood_group"] in compatible_groups
        assert donor["blood_group"] not in incompatible_groups


@pytest.mark.django_db
def test_donor_search_availability_gate(client):
    """
    Test that donors are filtered by NID status, manual toggle, and donation interval.
    """
    target_loc = cast("Location", LocationFactory(point=Point(90.0, 23.0)))
    bg = "A+"

    # 1. Not available toggle
    u1 = cast(
        "User",
        UserFactory(
            blood_group=bg,
            is_available_to_donate=False,
            is_phone_verified=True,
        ),
    )
    NIDVerificationFactory(user=u1, status=NIDVerification.Status.VERIFIED)
    u1.donor_profile.preferred_locations.add(target_loc)

    # 2. NID not verified
    u2 = cast(
        "User",
        UserFactory(
            blood_group=bg,
            is_available_to_donate=True,
            is_phone_verified=True,
        ),
    )
    NIDVerificationFactory(user=u2, status=NIDVerification.Status.PENDING)
    u2.donor_profile.preferred_locations.add(target_loc)

    # 3. Donated recently (within 120 days)
    u3 = cast(
        "User",
        UserFactory(
            blood_group=bg,
            is_available_to_donate=True,
            is_phone_verified=True,
            last_donation_date=timezone.now().date() - datetime.timedelta(days=30),
        ),
    )
    NIDVerificationFactory(user=u3, status=NIDVerification.Status.VERIFIED)
    u3.donor_profile.preferred_locations.add(target_loc)

    # 4. Resume date in future
    u4 = cast(
        "User",
        UserFactory(
            blood_group=bg,
            is_available_to_donate=True,
            is_phone_verified=True,
            resume_donation_date=timezone.now().date() + datetime.timedelta(days=10),
        ),
    )
    NIDVerificationFactory(user=u4, status=NIDVerification.Status.VERIFIED)
    u4.donor_profile.preferred_locations.add(target_loc)

    # 5. Valid donor
    u5 = cast(
        "User",
        UserFactory(
            username="01967251978",
            blood_group=bg,
            is_available_to_donate=True,
            is_phone_verified=True,
        ),
    )
    NIDVerificationFactory(user=u5, status=NIDVerification.Status.VERIFIED)
    u5.donor_profile.preferred_locations.add(target_loc)

    url = reverse("api:donors-list")
    response = client.get(url, {"blood_group": bg, "location_id": target_loc.id})

    assert response.status_code == HTTPStatus.OK
    results = response.json()
    assert len(results) == 1
    assert results[0]["id"] == str(u5.id)


@pytest.mark.django_db
def test_donor_search_proximity_sorting(client):
    """
    Test that results are sorted by physical distance.
    """
    bg = "O-"
    base_point = Point(90.0, 23.0)
    p_near = Point(90.001, 23.001)
    p_mid = Point(90.01, 23.01)
    p_far = Point(90.1, 23.1)

    loc_near = cast("Location", LocationFactory(point=p_near))
    loc_mid = cast("Location", LocationFactory(point=p_mid))
    loc_far = cast("Location", LocationFactory(point=p_far))

    # Create donors in reverse distance order
    d_far = cast(
        "User",
        UserFactory(
            username="01111111111",
            blood_group=bg,
            is_available_to_donate=True,
        ),
    )
    NIDVerificationFactory(user=d_far, status=NIDVerification.Status.VERIFIED)
    d_far.donor_profile.preferred_locations.add(loc_far)

    d_mid = cast(
        "User",
        UserFactory(
            username="01222222222",
            blood_group=bg,
            is_available_to_donate=True,
        ),
    )
    NIDVerificationFactory(user=d_mid, status=NIDVerification.Status.VERIFIED)
    d_mid.donor_profile.preferred_locations.add(loc_mid)

    d_near = cast(
        "User",
        UserFactory(
            username="01333333333",
            blood_group=bg,
            is_available_to_donate=True,
        ),
    )
    NIDVerificationFactory(user=d_near, status=NIDVerification.Status.VERIFIED)
    d_near.donor_profile.preferred_locations.add(loc_near)

    url = reverse("api:donors-list")
    response = client.get(
        url,
        {
            "blood_group": bg,
            "lat": base_point.y,
            "lng": base_point.x,
        },
    )

    assert response.status_code == HTTPStatus.OK
    results = response.json()

    expected_count = 3
    assert len(results) == expected_count
    assert results[0]["username"].startswith("013")
    assert results[1]["username"].startswith("012")
    assert results[2]["username"].startswith("011")


@pytest.mark.django_db
def test_donor_search_limit(client):
    """
    Test that search results are limited to top 5.
    """
    bg = "B+"
    target_loc = cast("Location", LocationFactory(point=Point(90.0, 23.0)))

    # Create 10 valid donors
    for i in range(10):
        user = cast(
            "User",
            UserFactory(
                username=f"015555555{i:02d}",
                blood_group=bg,
                is_available_to_donate=True,
                is_phone_verified=True,
            ),
        )
        NIDVerificationFactory(user=user, status=NIDVerification.Status.VERIFIED)
        user.donor_profile.preferred_locations.add(target_loc)

    url = reverse("api:donors-list")
    response = client.get(url, {"blood_group": bg, "location_id": target_loc.id})

    assert response.status_code == HTTPStatus.OK
    results = response.json()
    max_results = 5
    assert len(results) == max_results
