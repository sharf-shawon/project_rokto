from http import HTTPStatus

import pytest
from django.urls import reverse

from project_rokto.users.tests.factories import LocationFactory

pytestmark = pytest.mark.django_db


def test_preferred_locations_search_api(client):
    """
    Test that the location search API works for the preferred locations field.
    """
    LocationFactory(area_name="Gulshan", station="Gulshan", post_code="1212")
    LocationFactory(area_name="Banani", station="Gulshan", post_code="1213")
    expected_locations_count = 2

    url = reverse("locations:location-list")

    # Search for Gulshan
    response = client.get(url, {"q": "Gulshan"})
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == expected_locations_count

    # Search for Banani
    response = client.get(url, {"q": "Banani"})
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["area_name"] == "Banani"


def test_preferred_locations_empty_query(client):
    """
    Test that the API returns locations even when query is empty.
    """
    LocationFactory(area_name="Test Area")
    url = reverse("locations:location-list")

    response = client.get(url, {"q": ""})
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    # By my refactor, list() should return [:20] of all locations if q is empty
    assert len(data) >= 1


def test_location_search_division(client):
    """
    Test that the search works for the division field.
    """
    LocationFactory(area_name="Banani", division="Dhaka")
    url = reverse("locations:location-list")

    response = client.get(url, {"q": "Dhaka"})
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["division"] == "Dhaka"


def test_location_search_stripping(client):
    """
    Test that the search query is stripped of whitespace.
    """
    LocationFactory(area_name="Banani")
    url = reverse("locations:location-list")

    response = client.get(url, {"q": " Banani  "})
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["area_name"] == "Banani"
