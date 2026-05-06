from django.urls import path

from .views import blood_request_dashboard_view
from .views import confirm_donation_view
from .views import donor_response_view

app_name = "blood_requests"

urlpatterns = [
    path("dashboard/", blood_request_dashboard_view, name="dashboard"),
    path(
        "respond/<uuid:token>/<str:action_type>/",
        donor_response_view,
        name="donor_response",
    ),
    path(
        "confirm/<uuid:token>/<str:actor>/<str:status_type>/",
        confirm_donation_view,
        name="confirm_donation",
    ),
]
