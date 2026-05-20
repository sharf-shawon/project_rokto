from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.urls import reverse

from config import celery_app
from project_rokto.donors.models import Donor
from project_rokto.notifications.services import UnifiedNotificationService

from .models import Organization
from .services import SMSService

User = get_user_model()


@celery_app.task
def send_email_task(user_id, template_name, context, donor_id=None):
    donor = Donor.objects.get(pk=donor_id) if donor_id else None

    # Render message for the unified log
    message = render_to_string(
        f"notifications/email/{template_name}.html", context
    ).strip()

    UnifiedNotificationService.send(
        channel="EMAIL",
        message=message,
        donor=donor,
    )


@celery_app.task
def send_sms_task(user_id, template_name, context, organization_id=None, donor_id=None):
    user = User.objects.get(pk=user_id)
    org = Organization.objects.get(pk=organization_id) if organization_id else None
    donor = Donor.objects.get(pk=donor_id) if donor_id else None

    # SMSService.send already refactored to call UnifiedNotificationService
    return SMSService.send(user, template_name, context, org, donor=donor)


@celery_app.task
def send_push_task(user_id, template_name, context, donor_id=None):
    donor = Donor.objects.get(pk=donor_id) if donor_id else None

    # Render message for the unified log
    message = render_to_string(
        f"notifications/push/{template_name}.json", context
    ).strip()

    UnifiedNotificationService.send(
        channel="WEBPUSH",
        message=message,
        donor=donor,
    )


def send_donor_invite(donor_id, organization_id):
    """
    Unified entry point for sending donor invitations.
    """
    try:
        donor = Donor.objects.get(pk=donor_id)
        organization = Organization.objects.get(pk=organization_id)
    except Donor.DoesNotExist, Organization.DoesNotExist:
        return False, "Donor or Organization not found"

    invite_path = reverse("users:signup_info")
    invite_url = f"{settings.BASE_URL}{invite_path}?token={donor.invite_token}"

    context = {
        "organization_name": organization.name,
        "invite_url": invite_url,
    }

    # If donor is already linked to a user, we notify the user via dispatcher.
    if donor.user:
        from .services import NotificationDispatcher  # noqa: PLC0415

        NotificationDispatcher.send(donor.user, "donor_invite", context, organization)
        # Note: Dispatcher calls async tasks, so we return True here.
        return True, None

    # For Guest Donors, we send SMS directly.
    mock_user = User(phone_number=donor.phone_number, username=str(donor.phone_number))
    success, reason = SMSService.send(
        mock_user, "donor_invite", context, organization, donor=donor
    )
    if success:
        donor.invite_status = Donor.InviteStatus.SENT
        donor.save(update_fields=["invite_status"])
    return success, reason
