import datetime
import secrets

from django.utils import timezone

from .models import OTPRequest


class SMSAuthenticator:
    """
    Custom SMS Authenticator implementation for allauth.mfa
    """

    def __init__(self, user):
        self.user = user

    def send_otp(self):
        if not self.user.phone_number:
            return False

        otp_code = "".join(str(secrets.randbelow(10)) for _ in range(6))
        OTPRequest.objects.create(
            phone_number=self.user.phone_number,
            otp_code=otp_code,
            expires_at=timezone.now() + datetime.timedelta(minutes=5),
        )
        # In a real app, send the SMS here.
        # TODO: print(f"DEBUG: SMS OTP for {self.user.username}: {otp_code}")
        return True

    def validate_otp(self, code):
        try:
            otp_request = OTPRequest.objects.filter(
                phone_number=self.user.phone_number,
                otp_code=code,
                is_used=False,
            ).latest("created_at")

            if otp_request.is_valid():
                otp_request.is_used = True
                otp_request.save()
                otp_request.delete()
                return True
        except OTPRequest.DoesNotExist:
            pass
        return False
