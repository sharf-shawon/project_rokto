import csv
import io
import warnings
from typing import Any
from typing import cast

from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from pywebpush import WebPushException
from pywebpush import webpush

from project_rokto.donors.models import Donor
from project_rokto.donors.models import OrganizationDonorData
from project_rokto.notifications.models import SMSLog
from project_rokto.notifications.services import UnifiedNotificationService
from project_rokto.users.models import NotificationPreference

from .models import NotificationQuota

# HTTP 410 Gone indicates that the subscription has expired or is no longer valid.
HTTP_410_GONE = 410
BD_PHONE_DIGITS = 11


class QuotaService:
    @staticmethod
    def can_send_notification(organization, donor, channel):
        """
        Checks if a notification can be sent based on:
        1. User Cool-off period (Redis)
        2. Global Quota
        3. Organization Quota
        """
        # 1. User Cool-off check (Redis)
        if donor and donor.phone_number:
            cache_key = f"cooloff:{donor.phone_number}:{channel}"
            if cache.get(cache_key):
                return False, f"Cool-off period active for {donor.phone_number}"

        # 2. Check Global Quota
        global_quota = NotificationQuota.objects.filter(
            organization__isnull=True, channel=channel
        ).first()
        if global_quota and not QuotaService._is_within_limits(global_quota):
            return False, "Global quota exceeded"

        # 3. Check Organization Quota
        if organization:
            org_quota = NotificationQuota.objects.filter(
                organization=organization, channel=channel
            ).first()
            if org_quota and not QuotaService._is_within_limits(org_quota):
                return False, f"Organization quota exceeded for {organization.name}"

        return True, None

    @staticmethod
    def _is_within_limits(quota):
        return (
            quota.current_daily_usage < quota.daily_limit
            and quota.current_weekly_usage < quota.weekly_limit
            and quota.current_monthly_usage < quota.monthly_limit
        )


class DonorImportService:
    @staticmethod
    def import_from_csv(organization, csv_file) -> dict[str, Any]:
        """
        Parses a CSV file and imports donors, linking them to the organization.
        Expected CSV headers: phone_number, name, blood_group
        """
        if hasattr(csv_file, "read"):
            decoded_file = csv_file.read().decode("utf-8")
        else:
            decoded_file = csv_file.decode("utf-8")

        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        results: dict[str, Any] = {
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": [],
        }

        for row in reader:
            phone = row.get("phone_number")
            name = row.get("name")
            blood_group = row.get("blood_group")

            if not phone:
                results["skipped"] = cast("int", results["skipped"]) + 1
                continue

            try:
                # 1. Get or Create Donor by phone number (Unique Identity)
                donor, created = Donor.objects.get_or_create(
                    phone_number=phone, defaults={"blood_group": blood_group or ""}
                )

                # 2. Link to Organization and store Org-specific Guest Data
                # This ensures Org A doesn't see Org B's uploaded name
                OrganizationDonorData.objects.get_or_create(
                    organization=organization,
                    donor=donor,
                    defaults={
                        "guest_name": name or "",
                    },
                )

                if created:
                    results["created"] = cast("int", results["created"]) + 1
                else:
                    results["updated"] = cast("int", results["updated"]) + 1

            except Exception as e:  # noqa: BLE001
                # Catch all to prevent one bad record from failing the whole import
                cast_errors = cast("list[str]", results["errors"])
                cast_errors.append(f"Error processing {phone}: {e!s}")

        return results


class NotificationDispatcher:
    """
    Main entry point for sending notifications.
    Routes to enabled channels based on user preferences and priority.
    """

    @staticmethod
    def send(
        recipient_user, template_name, context, organization=None, priority="NORMAL"
    ):
        """
        Routes a notification to appropriate channels based on user preferences.
        """

        # 1. Get user preferences and determine category/flags
        prefs, _ = NotificationPreference.objects.get_or_create(user=recipient_user)
        donor = getattr(recipient_user, "donor_profile", None)

        config = {
            "emergency": "emergency_alerts",
            "invite": "org_invites",
        }

        type_flag = config.get(
            next((k for k in config if k in template_name), "other"), "reminders"
        )

        # If user has disabled this type of alert globally, stop here
        if not getattr(prefs, type_flag, False):
            return

        # 2. Dispatch to enabled channels via tasks

        from .tasks import send_email_task  # noqa: PLC0415
        from .tasks import send_push_task  # noqa: PLC0415
        from .tasks import send_sms_task  # noqa: PLC0415

        channels = [
            ("SMS", "sms_enabled", send_sms_task),
            ("EMAIL", "email_enabled", send_email_task),
            ("WEBPUSH", "web_push_enabled", send_push_task),
        ]

        for channel_name, channel_flag, task in channels:
            if getattr(prefs, channel_flag):
                if channel_name == "SMS":
                    task.delay(
                        recipient_user.id,
                        template_name,
                        context,
                        organization.id if organization else None,
                        donor.id if donor else None,
                    )
                else:
                    task.delay(
                        recipient_user.id,
                        template_name,
                        context,
                        donor.id if donor else None,
                    )


class EmailService:
    @staticmethod
    def send(user, template_name, context, donor=None):
        subject = context.get("subject", "Project Rokto Notification")
        html_content = render_to_string(
            f"notifications/email/{template_name}.html", context
        )
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()


class SMSService:
    """
    Legacy SMSService — delegates to UnifiedSMSService.

    Kept for backward compatibility. All new code should use
    UnifiedSMSService directly.
    """

    @staticmethod
    def send(user, template_name, context, organization=None, donor=None):

        warnings.warn(
            "SMSService.send() is deprecated. Use UnifiedSMSService instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        message = render_to_string(
            f"notifications/sms/{template_name}.txt", context
        ).strip()

        # Determine category from template name
        if "emergency" in template_name:
            category = SMSLog.Category.EMERGENCY
        elif "invite" in template_name:
            category = SMSLog.Category.INVITE
        else:
            category = SMSLog.Category.OTHER

        # Quota checks
        actual_donor = donor or getattr(user, "donor_profile", None)
        can_send, reason = QuotaService.can_send_notification(
            organization,
            actual_donor,
            NotificationQuota.Channel.SMS,
        )

        if not can_send:
            UnifiedNotificationService.log_failure(
                channel="SMS",
                category=category,
                donor=actual_donor,
                organization=organization,
                reason=reason,
            )
            return False, reason

        # Use UnifiedNotificationService for the actual send
        return UnifiedNotificationService.send(
            channel="SMS",
            phone_number=str(user.phone_number),
            message=message,
            category=category,
            donor=actual_donor,
            organization=organization,
        )


class WebPushService:
    @staticmethod
    def send(user, template_name, context, donor=None):
        message_data = render_to_string(
            f"notifications/push/{template_name}.json", context
        )

        # Ensure we have a donor object for logging
        donor or getattr(user, "donor_profile", None)

        subscriptions = user.web_push_subscriptions.all()
        for sub in subscriptions:
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                    },
                    data=message_data,
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": f"mailto:{settings.DEFAULT_FROM_EMAIL}"},
                )
            except WebPushException as ex:
                if ex.response and ex.response.status_code == HTTP_410_GONE:
                    # Subscription has expired or is no longer valid
                    sub.delete()
                else:
                    # Log other errors
                    pass
