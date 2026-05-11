from django.contrib.gis import admin
from unfold.admin import ModelAdmin

from .models import Location


@admin.register(Location)
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
