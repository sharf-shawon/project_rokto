from project_rokto.donors.models import Donor
from project_rokto.organizations.models import NotificationQuota
from project_rokto.organizations.models import Organization
from project_rokto.organizations.services import QuotaService


def send_donor_invite(donor_id, organization_id, channel=NotificationQuota.Channel.SMS):
    """
    Dispatches an invite notification to a donor, subject to Quota enforcement.
    """
    try:
        donor = Donor.objects.get(pk=donor_id)
        organization = Organization.objects.get(pk=organization_id)
    except Donor.DoesNotExist, Organization.DoesNotExist:
        return False, "Donor or Organization not found"

    # 1. Quota Check (Global, Org, and User Cool-off)
    can_send, reason = QuotaService.can_send_notification(organization, donor, channel)
    if not can_send:
        QuotaService.log_notification(organization, donor, channel, "BLOCKED", reason)
        return False, reason

    # 2. Dispatch (Implementation Placeholder)
    try:
        # In a real app, integrate with SMS/Email gateway here.
        # The invite link would use donor.invite_token.
        # e.g., f"https://rokto.org/invite/{donor.invite_token}"

        # TODO: integrate_with_actual_gateway(donor.phone_number, channel)

        status = "SENT"
        QuotaService.log_notification(organization, donor, channel, status)

        # Update donor invite status
        donor.invite_status = Donor.InviteStatus.SENT
        donor.save(update_fields=["invite_status"])

    except Exception as e:  # noqa: BLE001
        status = "FAILED"
        QuotaService.log_notification(organization, donor, channel, status, str(e))
        return False, str(e)
    else:
        return True, None
