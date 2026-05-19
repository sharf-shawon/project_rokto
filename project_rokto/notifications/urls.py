from django.http import Http404
from django.http import HttpResponsePermanentRedirect
from django.urls import path

from .url_shortener import resolve_short_code


def short_url_redirect(request, code):
    """Resolve a short code and redirect (302) to the original URL."""
    original_url = resolve_short_code(code)
    if original_url is None:
        msg = "Short URL not found or expired."
        raise Http404(msg)
    return HttpResponsePermanentRedirect(original_url)


app_name = "notifications"

urlpatterns = [
    path("<str:code>/", short_url_redirect, name="short_url_redirect"),
]
