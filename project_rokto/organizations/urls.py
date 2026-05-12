from django.urls import path

from .views import CreateOrganizationView
from .views import OrganizationDetailView
from .views import OrganizationListView

app_name = "organizations"
urlpatterns = [
    path("", OrganizationListView.as_view(), name="list"),
    path("create/", CreateOrganizationView.as_view(), name="create"),
    path("<slug:slug>/", OrganizationDetailView.as_view(), name="detail"),
]
