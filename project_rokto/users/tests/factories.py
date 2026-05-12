from __future__ import annotations

# mypy: ignore-errors
from django.contrib.gis.geos import Point
from factory import Faker
from factory import SubFactory
from factory import post_generation
from factory.django import DjangoModelFactory
from factory.django import ImageField

from project_rokto.donors.models import Donor
from project_rokto.locations.models import Location
from project_rokto.users.models import NIDVerification
from project_rokto.users.models import OTPRequest
from project_rokto.users.models import User


class LocationFactory(DjangoModelFactory[Location]):
    post_code = Faker("postcode")
    area_name = Faker("city")
    station = Faker("city")
    district = Faker("city")
    division = Faker("state")
    point = Point(0, 0)

    class Meta:
        model = Location


class UserFactory(DjangoModelFactory[User]):
    username = Faker("user_name")
    email = Faker("email")
    name = Faker("name")
    phone_number = Faker("numerify", text="017########")
    is_phone_verified = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Fields to look for and remove from kwargs
        donor_fields = [
            "blood_group",
            "is_available_to_donate",
            "last_donation_date",
            "resume_donation_date",
            "date_of_birth",
            "allergies",
            "health_conditions",
        ]
        donor_kwargs = {}
        for field in donor_fields:
            if field in kwargs:
                donor_kwargs[field] = kwargs.pop(field)

        user = super()._create(model_class, *args, **kwargs)

        # We store them on the instance temporarily for post_generation
        user._donor_kwargs = donor_kwargs  # noqa: SLF001
        return user

    @post_generation
    def password(self: User, create: bool, extracted: str | None, **kwargs):  # noqa: FBT001
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)
        if create:
            self.save()

    @post_generation
    def donor_profile(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.donor_profile = extracted
            return

        donor_kwargs = getattr(self, "_donor_kwargs", {})

        # Create donor profile if any donor fields were provided or by default
        Donor.objects.get_or_create(user=self, defaults=donor_kwargs)
        if hasattr(self, "_donor_kwargs"):
            delattr(self, "_donor_kwargs")

    class Meta:
        model = User
        skip_postgeneration_save = True


class DonorFactory(DjangoModelFactory[Donor]):
    user = SubFactory("project_rokto.users.tests.factories.UserFactory")
    blood_group = "A+"
    is_available_to_donate = False

    class Meta:
        model = Donor


class OTPRequestFactory(DjangoModelFactory[OTPRequest]):
    phone_number = Faker("numerify", text="017########")
    otp_code = Faker("numerify", text="######")

    class Meta:
        model = OTPRequest


class NIDVerificationFactory(DjangoModelFactory[NIDVerification]):
    user = SubFactory("project_rokto.users.tests.factories.UserFactory")
    front_image = ImageField(color="blue")
    back_image = ImageField(color="red")
    status = NIDVerification.Status.PENDING

    class Meta:
        model = NIDVerification
