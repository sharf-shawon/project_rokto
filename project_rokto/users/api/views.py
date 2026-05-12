import contextlib
import uuid

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models import Case
from django.db.models import F
from django.db.models import IntegerField
from django.db.models import Value
from django.db.models import When
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet

from project_rokto.locations.models import Location
from project_rokto.users.models import User

from .serializers import DonorSearchSerializer
from .serializers import UserSerializer


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, uuid.UUID)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class DonorSearchViewSet(ReadOnlyModelViewSet):
    """
    ViewSet for searching donors based on blood group and proximity to a location.
    """

    queryset = User.objects.available_for_donation()
    serializer_class = DonorSearchSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        blood_group = self.request.query_params.get("blood_group")
        location_id = self.request.query_params.get("location_id")
        lat = self.request.query_params.get("lat")
        lng = self.request.query_params.get("lng")

        if blood_group:
            # Use compatibility matrix to find all potential donors
            compatible_groups = User.get_compatible_donors(blood_group)
            queryset = queryset.filter(blood_group__in=compatible_groups).annotate(
                compatibility_score=Case(
                    When(blood_group=blood_group, then=Value(1)),
                    default=Value(2),
                    output_field=IntegerField(),
                ),
            )
        else:
            queryset = queryset.annotate(
                compatibility_score=Value(100, output_field=IntegerField()),
            )

        target_point = None
        if lat and lng:
            with contextlib.suppress(ValueError):
                target_point = Point(float(lng), float(lat), srid=4326)

        # Apply location filter if provided
        if location_id:
            queryset = queryset.filter(preferred_locations__id=location_id)

        # Fallback to location's point if lat/lng not provided
        if not target_point and location_id:
            try:
                target_location = Location.objects.get(id=location_id)
                target_point = target_location.point
            except Location.DoesNotExist, ValueError:
                pass

        if target_point:
            queryset = (
                queryset.annotate(
                    distance=Distance(
                        "preferred_locations__point",
                        target_point,
                    ),
                )
                .annotate(distance_km=F("distance") / 1000.0)
                .order_by("compatibility_score", "distance")
            )
        else:
            queryset = queryset.order_by("compatibility_score")

        return queryset.distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # Apply limit here instead of get_queryset
        queryset = queryset[:5]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
