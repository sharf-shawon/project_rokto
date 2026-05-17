from django.core.management.base import BaseCommand
from django.utils import timezone

from project_rokto.organizations.models import NotificationQuota


class Command(BaseCommand):
    help = "Resets notification quotas based on daily, weekly, and monthly intervals."

    def handle(self, *args, **options):
        now = timezone.now()

        # 1. Reset Daily (Every day at midnight)
        NotificationQuota.objects.all().update(
            current_daily_usage=0, last_reset_daily=now
        )
        self.stdout.write(self.style.SUCCESS("Daily quotas reset."))

        # 2. Reset Weekly (Every Monday)
        if now.weekday() == 0:
            NotificationQuota.objects.all().update(
                current_weekly_usage=0, last_reset_weekly=now
            )
            self.stdout.write(self.style.SUCCESS("Weekly quotas reset."))

        # 3. Reset Monthly (1st of the month)
        if now.day == 1:
            NotificationQuota.objects.all().update(
                current_monthly_usage=0, last_reset_monthly=now
            )
            self.stdout.write(self.style.SUCCESS("Monthly quotas reset."))
