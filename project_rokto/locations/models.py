import uuid

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    post_code = models.CharField(_("Post Code"), max_length=10)
    area_name = models.CharField(_("Area Name"), max_length=100)
    station = models.CharField(_("Station/Upazila"), max_length=100)
    district = models.CharField(_("District"), max_length=100)
    division = models.CharField(_("Division"), max_length=100)
    point = models.PointField(_("Coordinates"), null=True, blank=True)

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")
        ordering = ["division", "district", "station", "area_name"]
        indexes = [
            models.Index(fields=["post_code"]),
            models.Index(fields=["area_name"]),
            models.Index(fields=["station"]),
            models.Index(fields=["district"]),
        ]

    def __str__(self):
        return f"{self.area_name}, {self.station}, {self.district} ({self.post_code})"

    @property
    def full_address(self):
        return (
            f"{self.area_name}, {self.station}, {self.district}, "
            f"{self.division} - {self.post_code}"
        )
