from http import HTTPStatus

import pytest
from django.urls import reverse

from project_rokto.users.tests.factories import LocationFactory

pytestmark = pytest.mark.django_db


def test_location_search_public(client):
    """
    Test that the location search API is accessible to the public.
    """
    LocationFactory(area_name="Dhaka", post_code="1200")
    LocationFactory(area_name="Chittagong", post_code="4000")

    url = reverse("locations:location-list")
    response = client.get(url, {"q": "Dhaka"})

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["area_name"] == "Dhaka"


def test_location_search_multiple_fields(client):
    """
    Test that the search works across area_name, station, and post_code.
    """
    LocationFactory(area_name="Banani", station="Gulshan", post_code="1213")

    url = reverse("locations:location-list")

    # Search by area
    assert len(client.get(url, {"q": "Banani"}).json()) == 1
    # Search by station
    assert len(client.get(url, {"q": "Gulshan"}).json()) == 1
    # Search by postcode
    assert len(client.get(url, {"q": "1213"}).json()) == 1
    # Search by non-matching string
    assert len(client.get(url, {"q": "Sylhet"}).json()) == 0


def test_location_search_limit(client):
    """
    Test that the search results are limited (e.g., to 20).
    """
    max_limit = 20
    for i in range(30):
        LocationFactory(area_name=f"Area {i}", post_code=f"10{i:02d}")

    url = reverse("locations:location-list")
    response = client.get(url, {"q": "Area"})

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) <= max_limit
