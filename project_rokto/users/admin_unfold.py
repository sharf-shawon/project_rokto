from allauth.account import admin as account_admin
from allauth.account.models import EmailAddress
from allauth.mfa import admin as mfa_admin
from allauth.mfa.models import Authenticator
from allauth.socialaccount import admin as socialaccount_admin
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.models import SocialToken
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.models import Group
from django.contrib.sites import admin as sites_admin
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken import admin as authtoken_admin
from rest_framework.authtoken.models import TokenProxy
from unfold.admin import ModelAdmin
from unfold.sites import UnfoldAdminSite


class ProjectRoktoAdminSite(UnfoldAdminSite):
    site_header = _("Project Rokto Control Panel")
    site_title = _("Rokto Admin")

    def get_sidebar_navigation(self, request):
        return [
            {
                "title": _("User Management"),
                "separator": True,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "person",
                        "link": "admin:users_user_changelist",
                    },
                    {
                        "title": _("Groups"),
                        "icon": "group",
                        "link": "admin:auth_group_changelist",
                    },
                ],
            },
            {
                "title": _("Blood Management"),
                "separator": True,
                "items": [
                    {
                        "title": _("Donors"),
                        "icon": "volunteer_activism",
                        "link": "admin:donors_donor_changelist",
                    },
                    {
                        "title": _("Blood Requests"),
                        "icon": "emergency",
                        "link": "admin:blood_requests_bloodrequest_changelist",
                    },
                    {
                        "title": _("Locations"),
                        "icon": "location_on",
                        "link": "admin:locations_location_changelist",
                    },
                ],
            },
            {
                "title": _("Organizations"),
                "separator": True,
                "items": [
                    {
                        "title": _("Organizations"),
                        "icon": "corporate_fare",
                        "link": "admin:organizations_organization_changelist",
                    },
                    {
                        "title": _("Members"),
                        "icon": "badge",
                        "link": "admin:organizations_organizationmember_changelist",
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
                        "link": "admin:organizations_notificationlog_changelist",
                    },
                    {
                        "title": _("Notification Quotas"),
                        "icon": "bar_chart",
                        "link": "admin:organizations_notificationquota_changelist",
                    },
                ],
            },
        ]


admin_site = ProjectRoktoAdminSite(name="admin")

# Unregister default admin classes
admin.site.unregister(Group)
admin.site.unregister(Site)
admin.site.unregister(EmailAddress)
admin.site.unregister(Authenticator)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialApp)
admin.site.unregister(SocialToken)
admin.site.unregister(TokenProxy)


@admin.register(Group, site=admin_site)
class GroupAdmin(auth_admin.GroupAdmin, ModelAdmin):
    pass


@admin.register(Site, site=admin_site)
class SiteAdmin(sites_admin.SiteAdmin, ModelAdmin):
    pass


@admin.register(EmailAddress, site=admin_site)
class EmailAddressAdmin(account_admin.EmailAddressAdmin, ModelAdmin):
    pass


@admin.register(Authenticator, site=admin_site)
class AuthenticatorAdmin(mfa_admin.AuthenticatorAdmin, ModelAdmin):
    pass


@admin.register(SocialAccount, site=admin_site)
class SocialAccountAdmin(socialaccount_admin.SocialAccountAdmin, ModelAdmin):
    pass


@admin.register(SocialApp, site=admin_site)
class SocialAppAdmin(socialaccount_admin.SocialAppAdmin, ModelAdmin):
    pass


@admin.register(SocialToken, site=admin_site)
class SocialTokenAdmin(socialaccount_admin.SocialTokenAdmin, ModelAdmin):
    pass


@admin.register(TokenProxy, site=admin_site)
class TokenAdmin(authtoken_admin.TokenAdmin, ModelAdmin):
    pass
