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
from rest_framework.authtoken import admin as authtoken_admin
from rest_framework.authtoken.models import TokenProxy
from unfold.admin import ModelAdmin

# Unregister default admin classes
admin.site.unregister(Group)
admin.site.unregister(Site)
admin.site.unregister(EmailAddress)
admin.site.unregister(Authenticator)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialApp)
admin.site.unregister(SocialToken)
admin.site.unregister(TokenProxy)


@admin.register(Group)
class GroupAdmin(auth_admin.GroupAdmin, ModelAdmin):
    pass


@admin.register(Site)
class SiteAdmin(sites_admin.SiteAdmin, ModelAdmin):
    pass


@admin.register(EmailAddress)
class EmailAddressAdmin(account_admin.EmailAddressAdmin, ModelAdmin):
    pass


@admin.register(Authenticator)
class AuthenticatorAdmin(mfa_admin.AuthenticatorAdmin, ModelAdmin):
    pass


@admin.register(SocialAccount)
class SocialAccountAdmin(socialaccount_admin.SocialAccountAdmin, ModelAdmin):
    pass


@admin.register(SocialApp)
class SocialAppAdmin(socialaccount_admin.SocialAppAdmin, ModelAdmin):
    pass


@admin.register(SocialToken)
class SocialTokenAdmin(socialaccount_admin.SocialTokenAdmin, ModelAdmin):
    pass


@admin.register(TokenProxy)
class TokenAdmin(authtoken_admin.TokenAdmin, ModelAdmin):
    pass
