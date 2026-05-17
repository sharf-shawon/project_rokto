from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from project_rokto.blood_requests.views import BloodRequestViewSet
from project_rokto.organizations.api.views import OrganizationViewSet
from project_rokto.users.api.views import DonorSearchViewSet
from project_rokto.users.api.views import UserViewSet
from project_rokto.users.api.views import WebPushSubscriptionViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("donors", DonorSearchViewSet, basename="donors")
router.register("requests", BloodRequestViewSet, basename="requests")
router.register("organizations", OrganizationViewSet, basename="organizations")
router.register(
    "web-push-subscriptions",
    WebPushSubscriptionViewSet,
    basename="web-push-subscriptions",
)


app_name = "api"
urlpatterns = router.urls
