from rest_framework import serializers

from .models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "slug",
            "basic_info",
            "contact_information",
            "logo",
            "is_verified",
            "created_at",
        ]
