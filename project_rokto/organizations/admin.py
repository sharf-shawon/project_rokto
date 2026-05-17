from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.sites import UnfoldAdminSite

from project_rokto.users.admin_unfold import admin_site
from project_rokto.users.models import User

from .models import NotificationLog
from .models import NotificationQuota
from .models import Organization
from .models import OrganizationMember


class OrganizationAdminSite(UnfoldAdminSite):
    site_header = "Project Rokto Organization Management"
    site_title = "Org Admin"
    index_title = "Welcome to your Organization Dashboard"

    def get_sidebar_navigation(self, request):
        return [
            {
                "title": _("Organizations"),
                "separator": True,
                "items": [
                    {
                        "title": _("My Organization"),
                        "icon": "corporate_fare",
                        "link": "org_admin:organizations_organization_changelist",
                    },
                    {
                        "title": _("Team Members"),
                        "icon": "badge",
                        "link": "org_admin:organizations_organizationmember_changelist",
                    },
                ],
            },
            {
                "title": _("Donor Management"),
                "separator": True,
                "items": [
                    {
                        "title": _("Donors"),
                        "icon": "volunteer_activism",
                        "link": "org_admin:donors_donor_changelist",
                    },
                ],
            },
            {
                "title": _("Communications"),
                "separator": True,
                "items": [
                    {
                        "title": _("Notification Logs"),
                        "icon": "notifications",
                        "link": "org_admin:organizations_notificationlog_changelist",
                    },
                    {
                        "title": _("Notification Quotas"),
                        "icon": "bar_chart",
                        "link": "org_admin:organizations_notificationquota_changelist",
                    },
                ],
            },
        ]


org_admin_site = OrganizationAdminSite(name="org_admin")


class OrganizationAdminBase(ModelAdmin):
    list_display = ["name", "is_verified", "created_at"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Organization, site=org_admin_site)
class OrganizationOrgAdmin(OrganizationAdminBase):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(members__user=request.user)

    @action(description=_("Invite Manager"), url_path="invite-manager")
    def invite_manager(self, request, queryset):
        # This is a simplified invite: just add by username/phone
        if "apply" in request.POST:
            username = request.POST.get("username")
            role = request.POST.get("role", OrganizationMember.Role.MANAGER)
            try:
                user = User.objects.get(username=username)
                if not user.is_verified:
                    self.message_user(
                        request,
                        _("User must be fully verified to be a manager."),
                        messages.ERROR,
                    )
                else:
                    for org in queryset:
                        OrganizationMember.objects.get_or_create(
                            organization=org, user=user, defaults={"role": role}
                        )
                    self.message_user(
                        request, _("Manager invited successfully."), messages.SUCCESS
                    )
                return redirect(request.get_full_path())
            except User.DoesNotExist:
                self.message_user(request, _("User not found."), messages.ERROR)

        return render(
            request,
            "admin/organizations/invite_manager.html",
            context={"queryset": queryset},
        )


@admin.register(Organization, site=admin_site)
class OrganizationAdmin(OrganizationAdminBase):
    pass


class OrganizationMemberAdminBase(ModelAdmin):
    list_display = ["user", "organization", "role"]
    list_filter = ["role", "organization"]


@admin.register(OrganizationMember, site=org_admin_site)
class OrganizationMemberOrgAdmin(OrganizationMemberAdminBase):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Only show members of organizations the current user is an ADMIN of
        return qs.filter(
            organization__members__user=request.user,
            organization__members__role=OrganizationMember.Role.ADMIN,
        )

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj:
            return OrganizationMember.objects.filter(
                organization=obj.organization,
                user=request.user,
                role=OrganizationMember.Role.ADMIN,
            ).exists()
        return super().has_change_permission(request, obj)


@admin.register(OrganizationMember, site=admin_site)
class OrganizationMemberAdmin(OrganizationMemberAdminBase):
    pass


# ---------------------------------------------------------------------------
# NotificationLog Admin
# ---------------------------------------------------------------------------


class NotificationLogAdminBase(ModelAdmin):
    """Base admin for NotificationLog with shared display configuration."""

    list_display = [
        "channel",
        "status",
        "donor_link",
        "organization_link",
        "created_at",
    ]
    list_filter = ["channel", "status", "organization"]
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


# ---------------------------------------------------------------------------
# NotificationQuota Admin
# ---------------------------------------------------------------------------


class NotificationQuotaAdminBase(ModelAdmin):
    """Base admin for NotificationQuota with shared display configuration."""

    list_display = [
        "channel",
        "organization_link",
        "daily_limit",
        "current_daily_usage",
        "weekly_limit",
        "current_weekly_usage",
        "monthly_limit",
        "current_monthly_usage",
    ]
    list_filter = ["channel", "organization"]
    list_select_related = ["organization"]

    @admin.display(description=_("Organization"), ordering="organization__name")
    def organization_link(self, obj):
        """Display organization name."""
        return str(obj.organization) if obj.organization else "GLOBAL"


@admin.register(NotificationQuota, site=admin_site)
class NotificationQuotaAdmin(NotificationQuotaAdminBase):
    """Full-access admin for superusers."""


@admin.register(NotificationQuota, site=org_admin_site)
class NotificationQuotaOrgAdmin(NotificationQuotaAdminBase):
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
