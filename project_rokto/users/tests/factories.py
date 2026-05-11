from __future__ import annotations

import datetime

from django.contrib.gis.geos import Point
from django.utils import timezone
from factory import Faker
from factory import SubFactory
from factory import post_generation
from factory.django import DjangoModelFactory
from factory.django import ImageField

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
    blood_group = "A+"
    is_available_to_donate = False

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
    def preferred_locations(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for loc in extracted:
                self.preferred_locations.add(loc)

    class Meta:
        model = User
        django_get_or_create = ["username"]
        skip_postgeneration_save = True


class OTPRequestFactory(DjangoModelFactory[OTPRequest]):
    phone_number = Faker("numerify", text="017########")
    otp_code = Faker("numerify", text="######")
    expires_at = timezone.now() + datetime.timedelta(minutes=5)
    is_used = False

    class Meta:
        model = OTPRequest


class NIDVerificationFactory(DjangoModelFactory[NIDVerification]):
    user = SubFactory(UserFactory)
    front_image = ImageField(color="blue")
    back_image = ImageField(color="red")
    status = NIDVerification.Status.PENDING

    class Meta:
        model = NIDVerification
