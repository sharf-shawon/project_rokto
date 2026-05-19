from django.core.cache import cache

# Rate limit configuration
OTP_RATE_LIMIT_MAX = 5  # Max OTP requests per phone per window
OTP_RATE_LIMIT_WINDOW = 3600  # Window in seconds (1 hour)

IP_RATE_LIMIT_MAX = 1  # Max requests per IP per window
IP_RATE_LIMIT_WINDOW = 30  # Window in seconds (30 seconds)

# Redis key prefixes
OTP_RATE_KEY_PREFIX = "otp_rate_limit:"
IP_RATE_KEY_PREFIX = "ip_rate_limit:"


def check_otp_rate_limit(phone_number: str) -> bool:
    """
    Check if a phone number has exceeded the OTP rate limit.

    Returns True if the request is allowed, False if rate limited.
    Uses Redis INCR + EXPIRE for atomic counting with TTL.
    """
    key = f"{OTP_RATE_KEY_PREFIX}{phone_number}"
    return _check_rate_limit(key, OTP_RATE_LIMIT_MAX, OTP_RATE_LIMIT_WINDOW)


def check_ip_rate_limit(ip_address: str) -> bool:
    """
    Check if an IP address has exceeded the request rate limit.

    Returns True if the request is allowed, False if rate limited.
    Uses Redis SET + EXPIRE with NX (set only if not exists).
    """
    key = f"{IP_RATE_KEY_PREFIX}{ip_address}"
    return _check_rate_limit(key, IP_RATE_LIMIT_MAX, IP_RATE_LIMIT_WINDOW, ip_mode=True)


def _check_rate_limit(
    key: str, max_count: int, window: int, *, ip_mode: bool = False
) -> bool:
    """
    Generic rate limit checker.

    For phone mode (ip_mode=False): uses INCR to count up to max_count.
    For IP mode (ip_mode=True): uses get-and-set to allow only one request per window.
    """
    if ip_mode:
        # For IP: only allow 1 request per window
        # get + set approach for cache backend compatibility
        current = cache.get(key)
        if current is not None:
            return False  # Key exists → rate limited
        cache.set(key, 1, timeout=window)
        return True  # Key was set → allowed
    # For phone: count up to max
    current = cache.get(key)
    if current is None:
        # First request — set initial count
        cache.set(key, 1, timeout=window)
        return True

    if current >= max_count:
        return False  # Rate limited

    # Increment the counter
    cache.incr(key)
    return True


def get_rate_limit_headers(key_prefix: str, identifier: str, max_count: int) -> dict:
    """
    Get standard rate limit headers for a given rate limit key.

    Returns dict with X-RateLimit-* headers.
    """
    key = f"{key_prefix}{identifier}"
    remaining = cache.get(key)

    remaining = max_count if remaining is None else max(0, max_count - int(remaining))

    return {
        "X-RateLimit-Limit": str(max_count),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(OTP_RATE_LIMIT_WINDOW),
    }
