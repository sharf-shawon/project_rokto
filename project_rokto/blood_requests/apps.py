from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BloodRequestsConfig(AppConfig):
    name = "project_rokto.blood_requests"
    verbose_name = _("Blood Requests")
