import csv
import io
from typing import Any
from typing import cast

from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django_mimsms.client import MiMSMSClient
from pywebpush import WebPushException
from pywebpush import webpush

from project_rokto.donors.models import Donor
from project_rokto.donors.models import OrganizationDonorData
from project_rokto.users.models import NotificationPreference

from .models import NotificationLog
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

    @staticmethod
    def log_notification(organization, donor, channel, status, reason=""):
        """
        Logs a notification, updates usage counters, and sets cool-off.
        """
        NotificationLog.objects.create(
            organization=organization,
            donor=donor,
            channel=channel,
            status=status,
            failure_reason=reason,
        )

        if status == "SENT":
            # 1. Set Cool-off in Redis (24 hours)
            if donor and donor.phone_number:
                cache_key = f"cooloff:{donor.phone_number}:{channel}"
                is_active = True
                cache.set(cache_key, is_active, timeout=86400)

            # 2. Update Global Quota
            NotificationQuota.objects.filter(
                organization__isnull=True, channel=channel
            ).update(
                current_daily_usage=models.F("current_daily_usage") + 1,
                current_weekly_usage=models.F("current_weekly_usage") + 1,
                current_monthly_usage=models.F("current_monthly_usage") + 1,
            )
            # 3. Update Org Quota
            if organization:
                NotificationQuota.objects.filter(
                    organization=organization, channel=channel
                ).update(
                    current_daily_usage=models.F("current_daily_usage") + 1,
                    current_weekly_usage=models.F("current_weekly_usage") + 1,
                    current_monthly_usage=models.F("current_monthly_usage") + 1,
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
    @staticmethod
    def send(
        recipient_user, template_name, context, organization=None, priority="NORMAL"
    ):
        """
        Main entry point for sending notifications.
        Routes to enabled channels based on user preferences and priority.
        """
        # Delay imports to avoid circular dependency
        from .tasks import send_email_task  # noqa: PLC0415
        from .tasks import send_push_task  # noqa: PLC0415
        from .tasks import send_sms_task  # noqa: PLC0415

        # 1. Get user preferences
        prefs, _ = NotificationPreference.objects.get_or_create(user=recipient_user)

        donor = getattr(recipient_user, "donor_profile", None)
        donor_id = donor.id if donor else None

        # 2. Determine channels based on type (mapped from template_name)
        # Emergency Alerts
        if "emergency" in template_name:
            if prefs.sms_enabled and prefs.emergency_alerts:
                send_sms_task.delay(
                    recipient_user.id,
                    template_name,
                    context,
                    organization.id if organization else None,
                    donor_id=donor_id,
                )
            if prefs.web_push_enabled and prefs.emergency_alerts:
                send_push_task.delay(
                    recipient_user.id, template_name, context, donor_id=donor_id
                )
            if prefs.email_enabled and prefs.emergency_alerts:
                send_email_task.delay(
                    recipient_user.id, template_name, context, donor_id=donor_id
                )

        # Org Invites
        elif "invite" in template_name:
            if prefs.sms_enabled and prefs.org_invites:
                send_sms_task.delay(
                    recipient_user.id,
                    template_name,
                    context,
                    organization.id if organization else None,
                    donor_id=donor_id,
                )
            if prefs.email_enabled and prefs.org_invites:
                send_email_task.delay(
                    recipient_user.id, template_name, context, donor_id=donor_id
                )

        # Reminders / Others
        else:
            if prefs.web_push_enabled and prefs.reminders:
                send_push_task.delay(
                    recipient_user.id, template_name, context, donor_id=donor_id
                )
            if prefs.email_enabled and prefs.reminders:
                send_email_task.delay(
                    recipient_user.id, template_name, context, donor_id=donor_id
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

        if donor:
            QuotaService.log_notification(None, donor, "EMAIL", "SENT")


class SMSService:
    @staticmethod
    def send(user, template_name, context, organization=None, donor=None):
        message = render_to_string(
            f"notifications/sms/{template_name}.txt", context
        ).strip()

        # Ensure we have a donor object for quota/cooloff checks
        actual_donor = donor or getattr(user, "donor_profile", None)

        # Check Quota
        can_send, reason = QuotaService.can_send_notification(
            organization,
            actual_donor,
            NotificationQuota.Channel.SMS,
        )

        if not can_send:
            QuotaService.log_notification(
                organization,
                actual_donor,
                NotificationQuota.Channel.SMS,
                "BLOCKED",
                reason,
            )
            return False, reason

        try:
            client = MiMSMSClient(
                settings.MIMSMS_USERNAME,
                settings.MIMSMS_API_KEY,
                settings.MIMSMS_SENDER_ID,
                api_url=settings.MIMSMS_API_URL,
            )
            number = str(user.phone_number)

            if not number.startswith("880") and len(number) == BD_PHONE_DIGITS:
                number = "88" + number  # Ensure number starts with country code

            client.send_sms(number, message)
            QuotaService.log_notification(organization, actual_donor, "SMS", "SENT")
        except Exception as e:  # noqa: BLE001
            QuotaService.log_notification(
                organization,
                actual_donor,
                "SMS",
                "FAILED",
                str(e),
            )
            return False, str(e)
        else:
            return True, None


class WebPushService:
    @staticmethod
    def send(user, template_name, context, donor=None):
        message_data = render_to_string(
            f"notifications/push/{template_name}.json", context
        )

        # Ensure we have a donor object for logging
        actual_donor = donor or getattr(user, "donor_profile", None)

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
                if actual_donor:
                    QuotaService.log_notification(None, actual_donor, "WEBPUSH", "SENT")
            except WebPushException as ex:
                if ex.response and ex.response.status_code == HTTP_410_GONE:
                    # Subscription has expired or is no longer valid
                    sub.delete()
                else:
                    # Log other errors
                    pass
