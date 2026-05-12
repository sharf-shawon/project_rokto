from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm
from unfold.contrib.import_export.forms import ImportForm

from project_rokto.organizations.admin import org_admin_site
from project_rokto.users.admin_unfold import admin_site

from .models import Donor


class DonorAdminBase(ModelAdmin, ImportExportModelAdmin):
    list_display = ["get_name", "blood_group", "is_available_to_donate", "organization"]
    list_filter = ["blood_group", "is_available_to_donate", "organization"]
    search_fields = ["user__name", "user__username", "phone_number"]

    import_form_class = ImportForm
    export_form_class = ExportForm

    @admin.display(description=_("Name"))
    def get_name(self, obj):
        if obj.user:
            return obj.user.name or obj.user.username
        return obj.phone_number or "Guest Donor"


@admin.register(Donor, site=org_admin_site)
class DonorOrgAdmin(DonorAdminBase):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Filter donors by the organizations the user is a member of
        return qs.filter(organization__members__user=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.organization and not request.user.is_superuser:
            # Assign to the first organization the user is a member of if not specified
            first_org_membership = request.user.organization_memberships.first()
            if first_org_membership:
                obj.organization = first_org_membership.organization
        super().save_model(request, obj, form, change)


@admin.register(Donor, site=admin_site)
class DonorAdmin(DonorAdminBase):
    pass
