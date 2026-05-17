import uuid

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from project_rokto.locations.models import Location


class Donor(models.Model):
    class BloodGroup(models.TextChoices):
        A_POSITIVE = "A+", "A+"
        A_NEGATIVE = "A-", "A-"
        B_POSITIVE = "B+", "B+"
        B_NEGATIVE = "B-", "B-"
        O_POSITIVE = "O+", "O+"
        O_NEGATIVE = "O-", "O-"
        AB_POSITIVE = "AB+", "AB+"
        AB_NEGATIVE = "AB-", "AB-"

    class InviteStatus(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        SENT = "SENT", _("Sent")
        REGISTERED = "REGISTERED", _("Registered")
        BOUNCED = "BOUNCED", _("Bounced")

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donor_profile",
    )

    # Donor specific fields
    blood_group = models.CharField(
        _("Blood Group"),
        max_length=5,
        choices=BloodGroup.choices,
        blank=True,
    )
    last_donation_date = models.DateField(
        _("Last Blood Donation Date"),
        null=True,
        blank=True,
    )
    date_of_birth = models.DateField(_("Date of Birth"), null=True, blank=True)

    allergies = ArrayField(
        models.CharField(max_length=100),
        verbose_name=_("Allergies"),
        default=list,
        blank=True,
    )
    health_conditions = ArrayField(
        models.CharField(max_length=100),
        verbose_name=_("Known Health Conditions"),
        default=list,
        blank=True,
    )
    is_available_to_donate = models.BooleanField(
        _("Available to Donate"),
        default=False,
    )
    resume_donation_date = models.DateField(
        _("Date to Resume Donation"),
        null=True,
        blank=True,
    )
    preferred_locations = models.ManyToManyField(
        Location,
        verbose_name=_("Preferred Blood Donation Locations"),
        blank=True,
        related_name="donors",
    )

    phone_number = models.CharField(
        _("Phone Number"),
        max_length=15,
        blank=False,
        null=False,
        db_index=True,
    )

    invite_token = models.UUIDField(
        _("Invite Token"),
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    invite_status = models.CharField(
        _("Invite Status"),
        max_length=20,
        choices=InviteStatus.choices,
        default=InviteStatus.PENDING,
    )

    organizations: models.ManyToManyField = models.ManyToManyField(
        "organizations.Organization",
        through="OrganizationDonorData",
        related_name="donors",
        verbose_name=_("Organizations"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Donor")
        verbose_name_plural = _("Donors")

    def __str__(self):
        if self.user:
            return f"{self.user.name or self.user.username} ({self.blood_group})"
        return f"Guest Donor ({self.blood_group})"


class OrganizationDonorData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="donor_data",
    )
    donor = models.ForeignKey(
        "Donor",
        on_delete=models.CASCADE,
        related_name="organization_data",
    )

    guest_name = models.CharField(_("Guest Name"), max_length=255, blank=True)
    guest_notes = models.TextField(_("Guest Notes"), blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Organization Donor Data")
        verbose_name_plural = _("Organization Donor Data")
        unique_together = ["organization", "donor"]

    def __str__(self):
        return f"{self.guest_name or 'Guest'} - {self.organization.name}"
