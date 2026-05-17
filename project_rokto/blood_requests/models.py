import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class BloodRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    seeker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blood_requests_made",
        verbose_name=_("Seeker"),
    )
    reason = models.TextField(_("Reason for Request"))
    bags_needed = models.PositiveSmallIntegerField(
        _("Number of Bags Needed"),
        default=1,
    )
    donation_date = models.DateField(_("Proposed Donation Date"))
    hospital = models.CharField(_("Hospital/Location Name"), max_length=255)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Blood Request")
        verbose_name_plural = _("Blood Requests")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Request by {self.seeker.username} for {self.donation_date}"


class BloodRequestDonor(models.Model):
    class ResponseStatus(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        ACCEPTED = "ACCEPTED", _("Accepted")
        DECLINED = "DECLINED", _("Declined")

    class DonationConfirmation(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        YES = "YES", _("Yes")
        NO = "NO", _("No")

    blood_request = models.ForeignKey(
        BloodRequest,
        on_delete=models.CASCADE,
        related_name="donors",
        verbose_name=_("Blood Request"),
    )
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blood_requests_received",
        verbose_name=_("Donor"),
    )
    response_status = models.CharField(
        _("Response Status"),
        max_length=10,
        choices=ResponseStatus.choices,
        default=ResponseStatus.PENDING,
    )

    seeker_confirmation = models.CharField(
        _("Seeker Confirmation"),
        max_length=10,
        choices=DonationConfirmation.choices,
        default=DonationConfirmation.PENDING,
    )
    donor_confirmation = models.CharField(
        _("Donor Confirmation"),
        max_length=10,
        choices=DonationConfirmation.choices,
        default=DonationConfirmation.PENDING,
    )

    seeker_confirmation_at = models.DateTimeField(
        _("Seeker Confirmation At"),
        null=True,
        blank=True,
    )
    donor_confirmation_at = models.DateTimeField(
        _("Donor Confirmation At"),
        null=True,
        blank=True,
    )

    token = models.UUIDField(
        _("Secure Token"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    donor_contact_accessed_at = models.DateTimeField(
        _("Donor Contact Accessed At"),
        null=True,
        blank=True,
    )
    seeker_contact_accessed_at = models.DateTimeField(
        _("Seeker Contact Accessed At"),
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Blood Request Donor")
        verbose_name_plural = _("Blood Request Donors")
        unique_together = ["blood_request", "donor"]

    def __str__(self):
        return f"{self.donor.username} - {self.response_status}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_fully_confirmed:
            self.update_donor_profile()

    @property
    def is_fully_confirmed(self):
        return (
            self.seeker_confirmation == self.DonationConfirmation.YES
            and self.donor_confirmation == self.DonationConfirmation.YES
        )

    def update_donor_profile(self):
        """
        Updates the donor's last donation date if this request is fully confirmed.
        """
        donor_profile = self.donor.donor_profile
        request_date = self.blood_request.donation_date

        if (
            not donor_profile.last_donation_date
            or request_date >= donor_profile.last_donation_date
        ):
            if donor_profile.last_donation_date != request_date:
                donor_profile.last_donation_date = request_date
                donor_profile.save(update_fields=["last_donation_date"])
