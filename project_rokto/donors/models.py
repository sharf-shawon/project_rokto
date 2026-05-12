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

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donors",
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
