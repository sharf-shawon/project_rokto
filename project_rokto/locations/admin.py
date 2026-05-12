from django.contrib.gis import admin
from unfold.admin import ModelAdmin

from project_rokto.users.admin_unfold import admin_site

from .models import Location


@admin.register(Location, site=admin_site)
class LocationAdmin(ModelAdmin):
    list_display = (
        "area_name",
        "post_code",
        "station",
        "district",
        "division",
        "point",
    )
    list_filter = ("division", "district")
    search_fields = ("area_name", "post_code", "station", "district")
    ordering = ("division", "district", "station", "area_name")
