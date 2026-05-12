from django.contrib import admin
from unfold.admin import ModelAdmin

from project_rokto.users.admin_unfold import admin_site

from .models import BloodRequest
from .models import BloodRequestDonor


@admin.register(BloodRequest, site=admin_site)
class BloodRequestAdmin(ModelAdmin):
    list_display = [
        "seeker",
        "hospital",
        "bags_needed",
        "donation_date",
    ]
    list_filter = ["donation_date"]
    search_fields = ["hospital", "seeker__username", "seeker__phone_number"]


@admin.register(BloodRequestDonor, site=admin_site)
class BloodRequestDonorAdmin(ModelAdmin):
    list_display = [
        "blood_request",
        "donor",
        "response_status",
        "seeker_confirmation",
        "donor_confirmation",
    ]
    list_filter = ["response_status", "seeker_confirmation", "donor_confirmation"]
    search_fields = [
        "donor__username",
        "donor__phone_number",
        "blood_request__hospital",
    ]
