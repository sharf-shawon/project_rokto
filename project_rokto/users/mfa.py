import datetime
import secrets

from django.utils import timezone

from project_rokto.notifications.services import UnifiedNotificationService

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
        # Send the OTP via the unified notification service
        success, _ = UnifiedNotificationService.send_otp(
            phone_number=self.user.phone_number,
            otp_code=otp_code,
            donor=getattr(self.user, "donor_profile", None),
        )
        return success

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
