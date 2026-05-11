import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from project_rokto.blood_requests.models import BloodRequestDonor


class Command(BaseCommand):
    help = "Send post-donation verification emails to seekers and donors"

    def handle(self, *args, **options):
        # We look for ACCEPTED requests where donation_date was 2 days ago
        # and confirmations are still PENDING.
        two_days_ago = timezone.now().date() - datetime.timedelta(days=2)

        entries = BloodRequestDonor.objects.filter(
            response_status=BloodRequestDonor.ResponseStatus.ACCEPTED,
            blood_request__donation_date=two_days_ago,
            seeker_confirmation=BloodRequestDonor.DonationConfirmation.PENDING,
            donor_confirmation=BloodRequestDonor.DonationConfirmation.PENDING,
        )

        count = 0
        for entry in entries:
            self.send_followup_notifications(entry)
            count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Sent follow-up notifications for {count} entries."),
        )

    def send_followup_notifications(self, entry):
        seeker = entry.blood_request.seeker
        donor = entry.donor

        # Notify Seeker
        self.stdout.write(
            f"DEBUG: Follow-up to Seeker {seeker.username} "
            f"for request {entry.blood_request.id}",
        )
        # Links: /requests/confirm/<token>/seeker/yes/ or /no/

        # Notify Donor
        self.stdout.write(
            f"DEBUG: Follow-up to Donor {donor.username} "
            f"for request {entry.blood_request.id}",
        )
        # Links: /requests/confirm/<token>/donor/yes/ or /no/
