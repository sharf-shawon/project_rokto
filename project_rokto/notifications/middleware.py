import contextlib

from django.http import HttpResponse
from django.urls import reverse

from .rate_limiter import IP_RATE_KEY_PREFIX
from .rate_limiter import IP_RATE_LIMIT_MAX
from .rate_limiter import check_ip_rate_limit
from .rate_limiter import get_rate_limit_headers

# Paths that generate OTP requests — subject to IP rate limiting
OTP_GENERATING_PATHS = [
    "users:phone_login",
    "users:phone_add",
    "users:phone_manage",
]


class OTPRateLimitMiddleware:
    """
    Middleware that applies IP-based rate limiting to OTP-generating endpoints.

    Limits: 1 request per 30 seconds per IP address on POST requests
    to OTP-generating paths.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST":
            path_name = (
                request.resolver_match.url_name if request.resolver_match else None
            )

            # Build the set of OTP-generating URL names
            otp_url_names = set()
            for url_name in OTP_GENERATING_PATHS:
                with contextlib.suppress(Exception):
                    otp_url_names.add(reverse(url_name))

            # Check if current path is an OTP-generating path
            if path_name and any(name in request.path for name in otp_url_names):
                ip_address = self._get_client_ip(request)
                if not check_ip_rate_limit(ip_address):
                    response = HttpResponse(
                        "Too Many Requests. Please wait before requesting another OTP.",
                        status=429,
                        content_type="text/plain",
                    )
                    # Add rate limit headers
                    headers = get_rate_limit_headers(
                        IP_RATE_KEY_PREFIX, ip_address, IP_RATE_LIMIT_MAX
                    )
                    for key, value in headers.items():
                        response[key] = value
                    return response

        response = self.get_response(request)

        # Add rate limit headers to responses for OTP-generating paths
        if request.method == "POST":
            path_name = (
                request.resolver_match.url_name if request.resolver_match else None
            )
            ip_address = self._get_client_ip(request)
            headers = get_rate_limit_headers(
                IP_RATE_KEY_PREFIX, ip_address, IP_RATE_LIMIT_MAX
            )
            for key, value in headers.items():
                response[key] = value

        return response

    @staticmethod
    def _get_client_ip(request):
        """Extract the client IP address from the request."""
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "127.0.0.1")
