from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from .models import OTPRequest

User = get_user_model()


class PhoneOTPBackend(ModelBackend):
    """
    Authenticate a user using a phone number and a valid OTP.
    """

    def authenticate(self, request, phone_number=None, otp_code=None, **kwargs):  # type: ignore[override]
        if not phone_number or not otp_code:
            return None

        try:
            otp_request = OTPRequest.objects.filter(
                phone_number=phone_number,
                otp_code=otp_code,
                is_used=False,
            ).latest("created_at")

            if otp_request.is_valid():
                # Mark OTP as used
                otp_request.is_used = True
                otp_request.save()
                # Delete the OTP request after use for security
                otp_request.delete()

                # Get or create user
                user, created = User.objects.get_or_create(
                    phone_number=phone_number,
                    defaults={"username": phone_number, "is_phone_verified": True},
                )
                if not created and not user.is_phone_verified:
                    user.is_phone_verified = True
                    user.save()
                return user
        except OTPRequest.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
