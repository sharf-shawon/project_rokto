from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm
from unfold.contrib.import_export.forms import ImportForm

from project_rokto.organizations.admin import org_admin_site
from project_rokto.users.admin_unfold import admin_site

from .models import Donor
from .models import OrganizationDonorData


class DonorAdminBase(ModelAdmin, ImportExportModelAdmin):
    list_display = [
        "get_name",
        "blood_group",
        "is_available_to_donate",
        "get_organizations",
        "invite_status",
    ]
    list_filter = [
        "blood_group",
        "is_available_to_donate",
        "organizations",
        "invite_status",
    ]
    search_fields = ["user__name", "user__username", "phone_number"]

    import_form_class = ImportForm
    export_form_class = ExportForm

    @admin.display(description=_("Name"))
    def get_name(self, obj):
        if obj.user:
            return obj.user.name or obj.user.username
        return obj.phone_number or "Guest Donor"

    @admin.display(description=_("Organizations"))
    def get_organizations(self, obj):
        return ", ".join([org.name for org in obj.organizations.all()])


@admin.register(Donor, site=org_admin_site)
class DonorOrgAdmin(DonorAdminBase):
    def get_queryset(self, request):
        qs = super().get_queryset(request).prefetch_related("organizations")
        if request.user.is_superuser:
            return qs
        # Filter donors by the organizations the user is a member of
        return qs.filter(organizations__members__user=request.user).distinct()

    def save_model(self, request, obj, form, change):
        is_new = not change
        super().save_model(request, obj, form, change)

        if is_new and not request.user.is_superuser:
            # Assign to the first organization the user is a member of
            first_org_membership = request.user.organization_memberships.first()
            if first_org_membership:
                OrganizationDonorData.objects.get_or_create(
                    organization=first_org_membership.organization,
                    donor=obj,
                )


@admin.register(Donor, site=admin_site)
class DonorAdmin(DonorAdminBase):
    pass
