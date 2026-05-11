from rest_framework import serializers

from project_rokto.locations.serializers import LocationSerializer
from project_rokto.users.models import User
from project_rokto.users.utils import obfuscate_name
from project_rokto.users.utils import obfuscate_phone_number


class UserSerializer(serializers.ModelSerializer[User]):
    preferred_locations = LocationSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "name",
            "url",
            "phone_number",
            "blood_group",
            "is_available_to_donate",
            "preferred_locations",
        ]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"},
        }


class DonorSearchSerializer(serializers.ModelSerializer[User]):
    distance_km = serializers.FloatField(read_only=True)
    preferred_locations = LocationSerializer(many=True, read_only=True)
    username = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "name",
            "blood_group",
            "is_available_to_donate",
            "distance_km",
            "preferred_locations",
        ]

    def get_username(self, obj) -> str:
        return obfuscate_phone_number(obj.username)

    def get_name(self, obj) -> str:
        return obfuscate_name(obj.name)
