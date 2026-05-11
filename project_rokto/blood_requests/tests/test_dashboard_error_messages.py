from http import HTTPStatus

import pytest
from django.urls import reverse
from django.utils import timezone

from project_rokto.blood_requests.models import BloodRequest
from project_rokto.blood_requests.models import BloodRequestDonor
from project_rokto.blood_requests.tests.test_api import create_verified_user

pytestmark = pytest.mark.django_db


def test_confirm_donation_invalid_value(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor1")
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Test",
        bags_needed=1,
        donation_date=timezone.now().date(),
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=request,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
    )

    client.force_login(seeker)
    url = reverse("api:requests-confirm-donation", kwargs={"pk": entry.pk})
    response = client.post(
        url,
        {"confirmation": "INVALID"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Invalid confirmation value: INVALID"


def test_confirm_donation_already_confirmed(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor1")
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Test",
        bags_needed=1,
        donation_date=timezone.now().date(),
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=request,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
        seeker_confirmation=BloodRequestDonor.DonationConfirmation.YES,
    )

    client.force_login(seeker)
    url = reverse("api:requests-confirm-donation", kwargs={"pk": entry.pk})
    response = client.post(
        url,
        {"confirmation": "YES"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "You have already confirmed as YES"


def test_confirm_donation_unauthorized(client):
    seeker = create_verified_user()
    donor = create_verified_user(username="donor1")
    other_user = create_verified_user(username="other")
    request = BloodRequest.objects.create(
        seeker=seeker,
        reason="Test",
        bags_needed=1,
        donation_date=timezone.now().date(),
        hospital="H1",
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=request,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
    )

    client.force_login(other_user)
    url = reverse("api:requests-confirm-donation", kwargs={"pk": entry.pk})
    response = client.post(
        url,
        {"confirmation": "YES"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        response.json()["detail"] == "You are not authorized to confirm this donation."
    )
