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
