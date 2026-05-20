import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    name = models.CharField(_("Organization Name"), max_length=255)
    slug = models.SlugField(_("Slug"), max_length=255, unique=True, blank=True)

    logo = models.ImageField(_("Logo"), upload_to="orgs/logos/", blank=True, null=True)
    banner = models.ImageField(
        _("Banner"), upload_to="orgs/banners/", blank=True, null=True
    )

    basic_info = models.TextField(_("Basic Information"), blank=True)
    contact_information = models.TextField(_("Contact Information"), blank=True)

    is_verified = models.BooleanField(_("Is Verified"), default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class OrganizationMember(models.Model):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", _("Admin")
        MANAGER = "MANAGER", _("Manager")

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="members",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_memberships",
    )
    role = models.CharField(
        _("Role"),
        max_length=10,
        choices=Role.choices,
        default=Role.MANAGER,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Organization Member")
        verbose_name_plural = _("Organization Members")
        unique_together = ["organization", "user"]

    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"


class NotificationQuota(models.Model):
    class Channel(models.TextChoices):
        SMS = "SMS", _("SMS")
        EMAIL = "EMAIL", _("Email")
        WEBPUSH = "WEBPUSH", _("WebPush")

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="quotas",
        null=True,
        blank=True,  # Null represents Global Quota
    )
    channel = models.CharField(
        _("Channel"),
        max_length=10,
        choices=Channel.choices,
    )

    daily_limit = models.PositiveIntegerField(_("Daily Limit"), default=50)
    weekly_limit = models.PositiveIntegerField(_("Weekly Limit"), default=300)
    monthly_limit = models.PositiveIntegerField(_("Monthly Limit"), default=1000)

    current_daily_usage = models.PositiveIntegerField(
        _("Current Daily Usage"), default=0
    )
    current_weekly_usage = models.PositiveIntegerField(
        _("Current Weekly Usage"), default=0
    )
    current_monthly_usage = models.PositiveIntegerField(
        _("Current Monthly Usage"), default=0
    )

    last_reset_daily = models.DateTimeField(_("Last Daily Reset"), auto_now_add=True)
    last_reset_weekly = models.DateTimeField(_("Last Weekly Reset"), auto_now_add=True)
    last_reset_monthly = models.DateTimeField(
        _("Last Monthly Reset"), auto_now_add=True
    )

    class Meta:
        verbose_name = _("Notification Quota")
        verbose_name_plural = _("Notification Quotas")
        unique_together = ["organization", "channel"]

    def __str__(self):
        org_name = self.organization.name if self.organization else "GLOBAL"
        return f"{org_name} - {self.channel} Quota"
