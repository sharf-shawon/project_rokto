from http import HTTPStatus
from typing import TYPE_CHECKING
from typing import cast

import pytest
from django.urls import reverse
from django.utils import timezone

from project_rokto.blood_requests.models import BloodRequest
from project_rokto.blood_requests.models import BloodRequestDonor
from project_rokto.users.models import NIDVerification
from project_rokto.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from project_rokto.users.models import User

pytestmark = pytest.mark.django_db


def test_reveal_contact_invalid_actor(client):
    seeker = cast("User", UserFactory())
    donor = cast("User", UserFactory())
    today = timezone.now().date()
    br = BloodRequest.objects.create(
        seeker=seeker, bags_needed=1, hospital="H1", reason="R1", donation_date=today
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=br,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
    )

    client.force_login(seeker)
    url = reverse("api:requests-reveal-contact", kwargs={"pk": entry.pk})

    # Invalid actor type
    response = client.post(url, {"actor": "invalid"})
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_accept_request_invalid_status(client):
    donor = cast("User", UserFactory())
    today = timezone.now().date()
    br = BloodRequest.objects.create(
        seeker=cast("User", UserFactory()),
        bags_needed=1,
        hospital="H1",
        reason="R1",
        donation_date=today,
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=br,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
    )

    client.force_login(donor)
    url = reverse("api:requests-accept-request", kwargs={"pk": entry.pk})
    response = client.post(url)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "already been responded to" in response.data["detail"]


def test_decline_request_invalid_status(client):
    donor = cast("User", UserFactory())
    today = timezone.now().date()
    br = BloodRequest.objects.create(
        seeker=cast("User", UserFactory()),
        bags_needed=1,
        hospital="H1",
        reason="R1",
        donation_date=today,
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=br,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.DECLINED,
    )

    client.force_login(donor)
    url = reverse("api:requests-decline-request", kwargs={"pk": entry.pk})
    response = client.post(url)
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_confirm_donation_unauthorized_user(client):
    other_user = cast("User", UserFactory())
    today = timezone.now().date()
    br = BloodRequest.objects.create(
        seeker=cast("User", UserFactory()),
        bags_needed=1,
        hospital="H1",
        reason="R1",
        donation_date=today,
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=br, donor=cast("User", UserFactory())
    )

    client.force_login(other_user)
    url = reverse("api:requests-confirm-donation", kwargs={"pk": entry.pk})
    response = client.post(url, {"confirmation": "YES"})
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_donor_response_public_view_decline(client):
    today = timezone.now().date()
    br = BloodRequest.objects.create(
        seeker=cast("User", UserFactory()),
        bags_needed=1,
        hospital="H1",
        reason="R1",
        donation_date=today,
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=br, donor=cast("User", UserFactory())
    )

    url = reverse(
        "blood_requests:donor_response",
        kwargs={"token": entry.token, "action_type": "decline"},
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    entry.refresh_from_db()
    assert entry.response_status == BloodRequestDonor.ResponseStatus.DECLINED


def test_confirm_donation_public_view_already_confirmed(client):
    today = timezone.now().date()
    br = BloodRequest.objects.create(
        seeker=cast("User", UserFactory()),
        bags_needed=1,
        hospital="H1",
        reason="R1",
        donation_date=today,
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=br,
        donor=cast("User", UserFactory()),
        seeker_confirmation=BloodRequestDonor.DonationConfirmation.YES,
        donor_confirmation=BloodRequestDonor.DonationConfirmation.YES,
    )

    url = reverse(
        "blood_requests:confirm_donation",
        kwargs={"token": entry.token, "actor": "seeker", "status_type": "yes"},
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert "already fully confirmed" in response.content.decode()


def test_confirm_donation_public_view_invalid_actor(client):
    today = timezone.now().date()
    br = BloodRequest.objects.create(
        seeker=cast("User", UserFactory()),
        bags_needed=1,
        hospital="H1",
        reason="R1",
        donation_date=today,
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=br, donor=cast("User", UserFactory())
    )

    url = reverse(
        "blood_requests:confirm_donation",
        kwargs={"token": entry.token, "actor": "invalid", "status_type": "yes"},
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_sent_requests_api(client):
    seeker = cast("User", UserFactory())
    today = timezone.now().date()
    BloodRequest.objects.create(
        seeker=seeker, bags_needed=1, hospital="H1", reason="R1", donation_date=today
    )

    client.force_login(seeker)
    url = reverse("api:requests-sent-requests")
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert len(response.data) == 1


def test_received_requests_api(client):
    donor = cast("User", UserFactory())
    today = timezone.now().date()
    br = BloodRequest.objects.create(
        seeker=cast("User", UserFactory()),
        bags_needed=1,
        hospital="H1",
        reason="R1",
        donation_date=today,
    )
    BloodRequestDonor.objects.create(blood_request=br, donor=donor)

    client.force_login(donor)
    url = reverse("api:requests-received-requests")
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert len(response.data) == 1


def test_reveal_contact_not_accepted(client):
    seeker = cast("User", UserFactory())
    donor = cast("User", UserFactory())
    today = timezone.now().date()
    br = BloodRequest.objects.create(
        seeker=seeker, bags_needed=1, hospital="H1", reason="R1", donation_date=today
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=br,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.PENDING,
    )

    client.force_login(seeker)
    url = reverse("api:requests-reveal-contact", kwargs={"pk": entry.pk})
    response = client.post(url, {"actor": "seeker"})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "must be accepted" in response.data["detail"]


def test_reveal_contact_unauthorized_seeker(client):
    other_user = cast("User", UserFactory())
    seeker = cast("User", UserFactory())
    today = timezone.now().date()
    br = BloodRequest.objects.create(
        seeker=seeker, bags_needed=1, hospital="H1", reason="R1", donation_date=today
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=br,
        donor=cast("User", UserFactory()),
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
    )

    client.force_login(other_user)
    url = reverse("api:requests-reveal-contact", kwargs={"pk": entry.pk})
    response = client.post(url, {"actor": "seeker"})
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_reveal_contact_unauthorized_donor(client):
    other_user = cast("User", UserFactory())
    donor = cast("User", UserFactory())
    today = timezone.now().date()
    br = BloodRequest.objects.create(
        seeker=cast("User", UserFactory()),
        bags_needed=1,
        hospital="H1",
        reason="R1",
        donation_date=today,
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=br,
        donor=donor,
        response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
    )

    client.force_login(other_user)
    url = reverse("api:requests-reveal-contact", kwargs={"pk": entry.pk})
    response = client.post(url, {"actor": "donor"})
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_confirm_donation_public_view_already_confirmed_seeker(client):
    today = timezone.now().date()
    br = BloodRequest.objects.create(
        seeker=cast("User", UserFactory()),
        bags_needed=1,
        hospital="H1",
        reason="R1",
        donation_date=today,
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=br,
        donor=cast("User", UserFactory()),
        seeker_confirmation=BloodRequestDonor.DonationConfirmation.YES,
    )

    url = reverse(
        "blood_requests:confirm_donation",
        kwargs={"token": entry.token, "actor": "seeker", "status_type": "yes"},
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert "already confirmed this donation" in response.content.decode()


def test_confirm_donation_public_view_already_confirmed_donor(client):
    today = timezone.now().date()
    br = BloodRequest.objects.create(
        seeker=cast("User", UserFactory()),
        bags_needed=1,
        hospital="H1",
        reason="R1",
        donation_date=today,
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=br,
        donor=cast("User", UserFactory()),
        donor_confirmation=BloodRequestDonor.DonationConfirmation.YES,
    )

    url = reverse(
        "blood_requests:confirm_donation",
        kwargs={"token": entry.token, "actor": "donor", "status_type": "yes"},
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert "already confirmed this donation" in response.content.decode()


def test_cancel_request_api(client):
    seeker = cast("User", UserFactory())
    today = timezone.now().date()
    br = BloodRequest.objects.create(
        seeker=seeker, bags_needed=1, hospital="H1", reason="R1", donation_date=today
    )

    client.force_login(seeker)
    url = reverse("api:requests-cancel-request", kwargs={"pk": br.pk})
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK
    assert not BloodRequest.objects.filter(id=br.id).exists()


def test_create_blood_request_api(client):
    seeker = cast("User", UserFactory(is_phone_verified=True))
    NIDVerification.objects.create(user=seeker, status=NIDVerification.Status.VERIFIED)
    donor = cast("User", UserFactory())
    client.force_login(seeker)
    url = reverse("api:requests-list")

    response = client.post(
        url,
        {
            "reason": "Emergency",
            "bags_needed": 2,
            "donation_date": timezone.now().date(),
            "hospital": "City Hospital",
            "donor_ids": [str(donor.pk)],
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert BloodRequest.objects.filter(seeker=seeker).count() == 1


def test_donor_response_public_view_invalid_action(client):
    today = timezone.now().date()
    br = BloodRequest.objects.create(
        seeker=cast("User", UserFactory()),
        bags_needed=1,
        hospital="H1",
        reason="R1",
        donation_date=today,
    )
    entry = BloodRequestDonor.objects.create(
        blood_request=br, donor=cast("User", UserFactory())
    )

    url = reverse(
        "blood_requests:donor_response",
        kwargs={"token": entry.token, "action_type": "invalid"},
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.BAD_REQUEST
