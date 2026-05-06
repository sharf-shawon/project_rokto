import datetime

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from project_rokto.users.models import User
from project_rokto.users.utils import obfuscate_name
from project_rokto.users.utils import obfuscate_phone_number

from .models import BloodRequest
from .models import BloodRequestDonor


class BloodRequestDonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodRequestDonor
        fields = [
            "donor",
            "response_status",
            "seeker_confirmation",
            "donor_confirmation",
        ]
        read_only_fields = [
            "response_status",
            "seeker_confirmation",
            "donor_confirmation",
        ]


class BloodRequestSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodRequest
        fields = ["id", "hospital", "donation_date", "created_at"]


class BloodRequestDonorDashboardSerializer(serializers.ModelSerializer):
    donor_name = serializers.SerializerMethodField()
    donor_username = serializers.SerializerMethodField()
    seeker_name = serializers.SerializerMethodField()
    seeker_username = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    blood_request = BloodRequestSimpleSerializer(read_only=True)
    can_confirm = serializers.SerializerMethodField()
    is_fully_confirmed = serializers.BooleanField(read_only=True)

    class Meta:
        model = BloodRequestDonor
        fields = [
            "id",
            "donor_name",
            "donor_username",
            "seeker_name",
            "seeker_username",
            "response_status",
            "donor_contact_accessed_at",
            "seeker_contact_accessed_at",
            "phone_number",
            "blood_request",
            "seeker_confirmation",
            "donor_confirmation",
            "seeker_confirmation_at",
            "donor_confirmation_at",
            "can_confirm",
            "is_fully_confirmed",
        ]

    def get_donor_name(self, obj):
        return obfuscate_name(obj.donor.name)

    def get_donor_username(self, obj):
        return obfuscate_phone_number(obj.donor.username)

    def get_seeker_name(self, obj):
        return obfuscate_name(obj.blood_request.seeker.name)

    def get_seeker_username(self, obj):
        return obfuscate_phone_number(obj.blood_request.seeker.username)

    def get_phone_number(self, obj):
        user = self.context["request"].user
        # If user is seeker, they want donor's number
        if obj.blood_request.seeker == user:
            if obj.donor_contact_accessed_at:
                return obj.donor.phone_number
        # If user is donor, they want seeker's number
        elif obj.donor == user:
            if obj.seeker_contact_accessed_at:
                return obj.blood_request.seeker.phone_number
        return None

    def get_can_confirm(self, obj):
        return (
            obj.response_status == BloodRequestDonor.ResponseStatus.ACCEPTED
            and obj.blood_request.donation_date <= timezone.now().date()
        )


class BloodRequestDashboardSerializer(serializers.ModelSerializer):
    donors = BloodRequestDonorDashboardSerializer(many=True, read_only=True)

    class Meta:
        model = BloodRequest
        fields = [
            "id",
            "reason",
            "bags_needed",
            "donation_date",
            "hospital",
            "created_at",
            "donors",
        ]


class BloodRequestCreateSerializer(serializers.ModelSerializer):
    donor_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),
        write_only=True,
        max_length=3,
        min_length=1,
    )

    class Meta:
        model = BloodRequest
        fields = [
            "id",
            "reason",
            "bags_needed",
            "donation_date",
            "hospital",
            "donor_ids",
        ]

    def validate(self, data):
        seeker = self.context["request"].user
        # Seeker must be fully verified (Phone and NID)
        if not seeker.is_verified:
            raise serializers.ValidationError(
                _("You must verify your phone and NID before sending requests."),
                code="unverified_user",
            )

        # Rate limit: 1 request per 30 minutes
        thirty_minutes_ago = timezone.now() - datetime.timedelta(minutes=30)

        if BloodRequest.objects.filter(
            seeker=seeker,
            created_at__gte=thirty_minutes_ago,
        ).exists():
            raise serializers.ValidationError(
                _("You can only submit one blood donation request every 30 minutes."),
            )
        return data

    def create(self, validated_data):
        donor_ids = validated_data.pop("donor_ids")
        seeker = self.context["request"].user

        blood_request = BloodRequest.objects.create(seeker=seeker, **validated_data)

        for donor in donor_ids:
            BloodRequestDonor.objects.create(
                blood_request=blood_request,
                donor=donor,
            )

        return blood_request
