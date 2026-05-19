from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

from .models import NIDVerification


class VerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated or request.user.is_superuser:
            return self.get_response(request)

        path = request.path

        # Exact matches for exemption
        exact_exempt_urls = [
            "/",
            reverse("account_logout"),
            reverse("users:nid_submission"),
            reverse("users:phone_add"),
            reverse("users:phone_verify_otp"),
            reverse("users:detail", kwargs={"username": request.user.username}),
        ]

        # Prefix matches for exemption
        prefix_exempt_urls = [
            "/media/",
            "/static/",
            "/__debug__/",
            "/api/",
        ]

        # Add admin URL to prefix exempt URLs
        admin_url = "/" + settings.ADMIN_URL
        prefix_exempt_urls.append(admin_url)

        if path in exact_exempt_urls or any(
            path.startswith(url) for url in prefix_exempt_urls
        ):
            return self.get_response(request)

        # 1. Check NID Verification
        nid_verified = (
            hasattr(request.user, "nid_verification")
            and request.user.nid_verification.status == NIDVerification.Status.VERIFIED
        )

        if not nid_verified:
            return redirect("users:nid_submission")

        # 2. Check Phone Verification
        if not request.user.is_phone_verified:
            return redirect("users:phone_add")

        return self.get_response(request)
