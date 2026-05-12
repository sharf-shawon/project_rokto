from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm

# Apply Unfold theme to third-party models
from .admin_unfold import admin_site
from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import NIDVerification
from .models import OTPRequest
from .models import User

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


@admin.register(User, site=admin_site)
class UserAdmin(auth_admin.UserAdmin, ModelAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    change_password_form = AdminPasswordChangeForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {"fields": ("name", "email", "phone_number", "is_phone_verified")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = [
        "username",
        "name",
        "phone_number",
        "is_phone_verified",
        "is_superuser",
    ]
    search_fields = ["name", "phone_number", "username"]


@admin.register(OTPRequest, site=admin_site)
class OTPRequestAdmin(ModelAdmin):
    list_display = ["phone_number", "otp_code", "created_at", "expires_at", "is_used"]
    search_fields = ["phone_number"]
    readonly_fields = ["created_at"]


@admin.register(NIDVerification, site=admin_site)
class NIDVerificationAdmin(ModelAdmin):
    list_display = ["user", "status", "created_at", "updated_at"]
    list_filter = ["status"]
    search_fields = ["user__username", "user__phone_number"]
    actions = ["approve_verification", "reject_verification"]
    readonly_fields = ["created_at", "updated_at"]

    @admin.action(description=_("Approve selected NID verifications"))
    def approve_verification(self, request, queryset):
        queryset.update(status=NIDVerification.Status.VERIFIED)

    @admin.action(description=_("Reject selected NID verifications"))
    def reject_verification(self, request, queryset):
        queryset.update(status=NIDVerification.Status.REJECTED)
