from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from project_rokto.organizations.models import Organization
from project_rokto.organizations.models import OrganizationMember
from project_rokto.organizations.serializers import OrganizationSerializer
from project_rokto.organizations.services import DonorImportService


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Orgs the user is a member of
        user = self.request.user
        if user.is_authenticated:
            return Organization.objects.filter(members__user=user)
        return Organization.objects.none()

    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser])
    def upload_donors(self, request, pk=None):
        organization = self.get_object()

        # Ensure user has permission (Admin or Manager)
        if not OrganizationMember.objects.filter(
            organization=organization,
            user=request.user,
            role__in=[OrganizationMember.Role.ADMIN, OrganizationMember.Role.MANAGER],
        ).exists():
            return Response(
                {"error": "You do not have permission to upload donors for this org."},
                status=status.HTTP_403_FORBIDDEN,
            )

        csv_file = request.FILES.get("file")
        if not csv_file:
            return Response(
                {"error": "No file uploaded (key 'file' expected)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = DonorImportService.import_from_csv(organization, csv_file)
        return Response(results)
