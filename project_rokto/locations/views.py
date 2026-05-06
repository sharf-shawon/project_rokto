from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Location
from .serializers import LocationSerializer


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.query_params.get("q")
        if query:
            query = query.strip()
            queryset = queryset.filter(
                Q(area_name__icontains=query)
                | Q(station__icontains=query)
                | Q(district__icontains=query)
                | Q(post_code__icontains=query)
                | Q(division__icontains=query),
            )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # Apply limit here instead of get_queryset to avoid AssertionError
        # when DRF tries to filter/order the sliced queryset.
        queryset = queryset[:20]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
