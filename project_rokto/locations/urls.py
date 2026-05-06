from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import LocationViewSet

router = DefaultRouter()
router.register(r"search", LocationViewSet, basename="location")

app_name = "locations"
urlpatterns = [
    path("api/", include(router.urls)),
]
