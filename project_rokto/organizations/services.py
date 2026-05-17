import csv
import io
from typing import Any

from django.core.cache import cache
from django.db import models

from project_rokto.donors.models import Donor
from project_rokto.donors.models import OrganizationDonorData

from .models import NotificationLog
from .models import NotificationQuota


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
                results["skipped"] += 1
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
                    results["created"] += 1
                else:
                    results["updated"] += 1

            except Exception as e:  # noqa: BLE001
                # Catch all to prevent one bad record from failing the whole import
                cast_errors: list[str] = results["errors"]
                cast_errors.append(f"Error processing {phone}: {e!s}")

        return results
