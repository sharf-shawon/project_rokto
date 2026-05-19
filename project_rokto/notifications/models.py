import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class SMSLog(models.Model):
    """Central audit log for every outbound SMS, regardless of source."""

    class Category(models.TextChoices):
        OTP = "OTP", _("OTP Verification")
        EMERGENCY = "EMERGENCY", _("Emergency Blood Request")
        INVITE = "INVITE", _("Donor Invitation")
        OTHER = "OTHER", _("Other")

    class Status(models.TextChoices):
        SENT = "SENT", _("Sent")
        FAILED = "FAILED", _("Failed")
        BLOCKED = "BLOCKED", _("Blocked")
        TRUNCATED = "TRUNCATED", _("Truncated")

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    phone_number = models.CharField(_("Phone Number"), max_length=15, db_index=True)
    message = models.TextField(_("Message"))
    message_length = models.PositiveIntegerField(_("Message Length"), editable=False)
    original_length = models.PositiveIntegerField(
        _("Original Length (pre-truncation)"), null=True, blank=True
    )
    category = models.CharField(
        _("Category"), max_length=10, choices=Category.choices, db_index=True
    )
    provider_response = models.JSONField(_("Provider Response"), null=True, blank=True)
    status = models.CharField(
        _("Status"), max_length=10, choices=Status.choices, db_index=True
    )
    failure_reason = models.TextField(_("Failure Reason"), blank=True)
    related_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sms_logs",
    )
    related_organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sms_logs",
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _("SMS Log")
        verbose_name_plural = _("SMS Logs")
        ordering = ["-created_at"]

    def __str__(self):
        return f"SMS {self.status} to {self.phone_number} ({self.category})"

    def save(self, *args, **kwargs):
        self.message_length = len(self.message)
        if self.original_length is None:
            self.original_length = self.message_length
        super().save(*args, **kwargs)


class ShortURL(models.Model):
    """Self-hosted URL shortener for SMS link compression."""

    class Category(models.TextChoices):
        OTP = "OTP", _("OTP Verification")
        DONATION_ACCEPT = "DONATION_ACCEPT", _("Donation Accept Link")
        DONATION_DECLINE = "DONATION_DECLINE", _("Donation Decline Link")
        DONATION_CONFIRM = "DONATION_CONFIRM", _("Donation Confirm Link")
        INVITE = "INVITE", _("Donor Invitation")
        OTHER = "OTHER", _("Other")

    original_url = models.URLField(_("Original URL"), max_length=2048, unique=True)
    code = models.CharField(_("Short Code"), max_length=12, unique=True, db_index=True)
    category = models.CharField(
        _("Category"), max_length=20, choices=Category.choices, default=Category.OTHER
    )
    expires_at = models.DateTimeField(_("Expires At"), null=True, blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Short URL")
        verbose_name_plural = _("Short URLs")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} -> {self.original_url[:60]}..."

    @property
    def is_expired(self) -> bool:
        return self.expires_at is not None and self.expires_at < timezone.now()
