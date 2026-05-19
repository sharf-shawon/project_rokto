from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import ShortURL

# Default expiry durations in days
EXPIRY_DURATIONS: dict[str, int] = {
    ShortURL.Category.OTP: 1,  # OTP links expire in 1 day
    ShortURL.Category.DONATION_ACCEPT: 7,  # Donation links expire in 7 days
    ShortURL.Category.DONATION_DECLINE: 7,
    ShortURL.Category.DONATION_CONFIRM: 7,
    ShortURL.Category.INVITE: 30,  # Invite links expire in 30 days
    ShortURL.Category.OTHER: 30,
}


def _get_hashids():
    """Get a Hashids instance with a salt from settings."""
    from hashids import Hashids  # noqa: PLC0415

    salt = getattr(settings, "SHORT_URL_SALT", "project_rokto_default_salt")
    return Hashids(salt=salt, min_length=6)


def _get_short_url_domain() -> str:
    """Get the short URL domain from settings."""
    return getattr(settings, "SHORT_URL_DOMAIN", "").rstrip("/")


def shorten_url(
    original_url: str,
    category: str = ShortURL.Category.OTHER,
    expires_at=None,
) -> str:
    """
    Shorten a URL and return the short URL string.

    Deduplicates: same original_url always returns the same short code.
    If expires_at is None, a default expiry is computed based on category.
    """
    # Check if already shortened
    existing = ShortURL.objects.filter(original_url=original_url).first()
    if existing:
        return f"{_get_short_url_domain()}/{existing.code}/"

    # Compute default expiry
    if expires_at is None:
        days = EXPIRY_DURATIONS.get(category, 30)
        expires_at = timezone.now() + timedelta(days=days)

    # Create the ShortURL record (AutoField generates the id)
    obj = ShortURL.objects.create(
        original_url=original_url,
        code="",  # Will be updated below
        category=category,
        expires_at=expires_at,
    )

    # Generate hashid from the database id
    hashids = _get_hashids()
    code = hashids.encode(obj.id)

    # Update the code
    obj.code = code
    obj.save(update_fields=["code"])

    return f"{_get_short_url_domain()}/{code}/"


def resolve_short_code(code: str) -> str | None:
    """
    Resolve a short code to the original URL.

    Returns None if the code is unknown or expired.
    """
    try:
        obj = ShortURL.objects.get(code=code)
    except ShortURL.DoesNotExist:
        return None

    if obj.is_expired:
        return None

    return obj.original_url
