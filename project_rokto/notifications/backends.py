from django.conf import settings
from django_mimsms.client import MiMSMSClient

# Minimum length of a Bangladeshi phone number (11 digits)
BD_PHONE_DIGITS = 11


class MiMSMSBackend:
    """
    Provider backend for MiMSMS (Bangladesh SMS gateway).

    Wraps django-mimsms MiMSMSClient with a standardized interface.
    """

    def __init__(self):
        self._username = settings.MIMSMS_USERNAME
        self._api_key = settings.MIMSMS_API_KEY
        self._sender_id = settings.MIMSMS_SENDER_ID
        self._api_url = settings.MIMSMS_API_URL

    def send(self, phone_number: str, message: str) -> dict:
        """
        Send an SMS via MiMSMS.

        Args:
            phone_number: The recipient's phone number.
            message: The SMS message text.

        Returns:
            dict with keys:
                - status: "sent" on success
                - trxn_id: transaction ID from provider (if available)
                - provider_raw: full provider response

        Raises:
            Exception: If sending fails (caller handles logging).
        """
        # Ensure number starts with 88 country code
        number = str(phone_number)
        if not number.startswith("880") and len(number) == BD_PHONE_DIGITS:
            number = "88" + number

        client = MiMSMSClient(
            self._username,
            self._api_key,
            self._sender_id,
            api_url=self._api_url,
        )

        response = client.send_sms(number, message)

        return {
            "status": "sent",
            "trxn_id": response.trxn_id or "",
            "provider_raw": response.model_dump()
            if hasattr(response, "model_dump")
            else str(response),
        }
