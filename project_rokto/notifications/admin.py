from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from project_rokto.organizations.admin import org_admin_site
from project_rokto.users.admin_unfold import admin_site

from .models import NotificationLog
from .models import ShortURL
from .models import SMSLog


@admin.register(SMSLog)
class SMSLogAdmin(ModelAdmin):
    list_display = [
        "phone_number",
        "category",
        "status",
        "message_length",
        "related_user",
        "created_at",
    ]
    list_filter = ["category", "status", "created_at"]
    search_fields = ["phone_number", "message"]
    readonly_fields = [
        "phone_number",
        "message",
        "message_length",
        "original_length",
        "category",
        "provider_response",
        "status",
        "failure_reason",
        "related_user",
        "related_organization",
        "created_at",
    ]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False  # SMSLog is append-only via the service

    def has_change_permission(self, request, obj=None):
        return False  # SMSLog is read-only

    def has_delete_permission(self, request, obj=None):
        return False  # SMSLog is append-only


@admin.register(ShortURL)
class ShortURLAdmin(ModelAdmin):
    list_display = ["code", "category", "is_expired", "created_at"]
    list_filter = ["category", "created_at"]
    search_fields = ["code", "original_url"]
    readonly_fields = ["code", "created_at"]


# ---------------------------------------------------------------------------
# NotificationLog Admin
# ---------------------------------------------------------------------------


class NotificationLogAdminBase(ModelAdmin):
    """Base admin for NotificationLog with shared display configuration."""

    list_display = [
        "channel",
        "category",
        "status",
        "donor_link",
        "organization_link",
        "created_at",
    ]
    list_filter = ["channel", "category", "status", "organization"]
    search_fields = [
        "donor__phone_number",
    ]
    date_hierarchy = "created_at"
    list_select_related = ["donor", "organization"]

    @admin.display(description=_("Donor"), ordering="donor__phone_number")
    def donor_link(self, obj):
        """Display donor phone number."""
        return str(obj.donor) if obj.donor else "-"

    @admin.display(description=_("Organization"), ordering="organization__name")
    def organization_link(self, obj):
        """Display organization name."""
        return str(obj.organization) if obj.organization else "GLOBAL"


@admin.register(NotificationLog, site=admin_site)
class NotificationLogAdmin(NotificationLogAdminBase):
    """Full-access admin for superusers."""


@admin.register(NotificationLog, site=org_admin_site)
class NotificationLogOrgAdmin(NotificationLogAdminBase):
    """Read-only org-scoped admin for organization admins."""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(
            organization__members__user=request.user,
        ).distinct()

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
