import datetime
import uuid

from django.apps import apps
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import CharField
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from project_rokto.locations.models import Location

phone_validator = RegexValidator(
    regex=r"^(?:\+88|88)?(01[3-9]\d{8})$",
    message=_(
        "Enter a valid Bangladeshi phone number (e.g., +8801712345678 or 01712345678).",
    ),
)


class UserQuerySet(models.QuerySet):
    def available_for_donation(self):
        """
        Filters for users who are currently eligible to donate blood.
        - is_available_to_donate = True
        - NID status is VERIFIED
        - resume_donation_date is NULL or in the past
        - last_donation_date is NULL or >= 120 days ago
        """
        today = timezone.now().date()
        wait_period = today - datetime.timedelta(days=120)

        return (
            self.filter(
                is_available_to_donate=True,
                nid_verification__status=NIDVerification.Status.VERIFIED,
            )
            .filter(
                Q(resume_donation_date__isnull=True)
                | Q(resume_donation_date__lte=today),
            )
            .filter(
                Q(last_donation_date__isnull=True)
                | Q(last_donation_date__lte=wait_period),
            )
        )


class CustomUserManager(UserManager.from_queryset(UserQuerySet)):  # type: ignore[misc]
    pass


class User(AbstractUser):
    """
    Default custom user model for Project Rokto.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    MAX_VERIFICATION_ATTEMPTS = 3

    class BloodGroup(models.TextChoices):
        A_POSITIVE = "A+", "A+"
        A_NEGATIVE = "A-", "A-"
        B_POSITIVE = "B+", "B+"
        B_NEGATIVE = "B-", "B-"
        O_POSITIVE = "O+", "O+"
        O_NEGATIVE = "O-", "O-"
        AB_POSITIVE = "AB+", "AB+"
        AB_NEGATIVE = "AB-", "AB-"

    @classmethod
    def get_compatible_donors(cls, blood_group: str) -> list[str]:
        """
        Returns a list of blood groups that can donate to the given receiver
        blood group.
        """
        matrix = {
            "A+": ["A+", "A-", "O+", "O-"],
            "O+": ["O+", "O-"],
            "B+": ["B+", "B-", "O+", "O-"],
            "AB+": ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"],
            "A-": ["A-", "O-"],
            "O-": ["O-"],
            "B-": ["B-", "O-"],
            "AB-": ["AB-", "A-", "B-", "O-"],
        }
        return matrix.get(blood_group, [])

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)

    objects = CustomUserManager()  # type: ignore[misc]

    phone_number = CharField(
        _("Phone Number"),
        max_length=15,
        unique=True,
        validators=[phone_validator],
        blank=True,
        null=True,
    )
    is_phone_verified = models.BooleanField(_("Phone Verified"), default=False)
    verification_attempts = models.PositiveSmallIntegerField(
        _("Verification Attempts"),
        default=0,
    )

    # Profile fields
    date_of_birth = models.DateField(_("Date of Birth"), null=True, blank=True)
    blood_group = CharField(
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
        related_name="interested_donors",
    )

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    @property
    def is_verified(self) -> bool:
        """Check if user is fully verified (NID and Phone)."""
        return (
            self.is_phone_verified
            and hasattr(self, "nid_verification")
            and self.nid_verification.status == NIDVerification.Status.VERIFIED
        )

    @property
    def total_donations_confirmed(self):
        BloodRequestDonor = apps.get_model("blood_requests", "BloodRequestDonor")

        return self.blood_requests_received.filter(
            seeker_confirmation=BloodRequestDonor.DonationConfirmation.YES,
            donor_confirmation=BloodRequestDonor.DonationConfirmation.YES,
        ).count()

    @property
    def total_received_confirmed(self):
        BloodRequestDonor = apps.get_model("blood_requests", "BloodRequestDonor")

        return BloodRequestDonor.objects.filter(
            blood_request__seeker=self,
            seeker_confirmation=BloodRequestDonor.DonationConfirmation.YES,
            donor_confirmation=BloodRequestDonor.DonationConfirmation.YES,
        ).count()


class OTPRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    phone_number = CharField(max_length=15, validators=[phone_validator])
    otp_code = CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("OTP Request")
        verbose_name_plural = _("OTP Requests")

    def __str__(self):
        return f"OTP for {self.phone_number} at {self.created_at}"

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()


class NIDVerification(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        VERIFIED = "VERIFIED", _("Verified")
        REJECTED = "REJECTED", _("Rejected")

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="nid_verification",
    )
    front_image = models.ImageField(upload_to="nids/front/")
    back_image = models.ImageField(upload_to="nids/back/")
    status = CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    rejection_reason = CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("NID Verification")
        verbose_name_plural = _("NID Verifications")

    def __str__(self):
        return f"NID Verification for {self.user.username} ({self.status})"
