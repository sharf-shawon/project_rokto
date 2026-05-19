## 1. Create Notifications App & Models

- [x] 1.1 Create `project_rokto/notifications` app with `AppConfig`
- [x] 1.2 Add `notifications` to `INSTALLED_APPS` in `config/settings/base.py`
- [x] 1.3 Create `SMSLog` model: `id`, `phone_number`, `message`, `message_length`, `category` (OTP/EMERGENCY/INVITE/OTHER), `provider_response` (JSONField), `status` (SENT/FAILED/BLOCKED/TRUNCATED), `failure_reason`, `related_user` (FK User, nullable), `related_organization` (FK Organization, nullable), `created_at`
- [x] 1.4 Create `ShortURL` model: `id` (AutoField), `original_url` (URLField, unique), `code` (CharField, unique, indexed), `category` (CharField, choices), `expires_at` (DateTimeField, nullable), `created_at`
- [x] 1.5 Register `SMSLog` and `ShortURL` in `notifications/admin.py` with proper list views, filters, and search
- [x] 1.6 Run `makemigrations` and `migrate`

## 2. Implement Core Services

- [x] 2.1 Implement `url_shortener.py`: `shorten_url(original_url, category, expires_at=None) -> str` using hashids, with deduplication (same URL returns same code)
- [x] 2.2 Implement `url_shortener.py`: `resolve_short_code(code) -> str | None` for resolution
- [x] 2.3 Add a URL resolver view in `notifications/urls.py` that catches `/<code>/` and redirects (302) to the original URL, returning 404 for expired/unknown codes
- [x] 2.4 Implement `backends.py`: `MiMSMSBackend` class with `send(phone_number, message) -> dict` wrapping `django-mimsms` MiMSMSClient, returning `{"status": "sent", "trxn_id": "..."}` or raising
- [x] 2.5 Implement `rate_limiter.py`: `check_otp_rate_limit(phone_number) -> bool` — Redis INCR + EXPIRE, max 5/hour
- [x] 2.6 Implement `rate_limiter.py`: `check_ip_rate_limit(ip_address) -> bool` — Redis SET + EXPIRE (NX), max 1/30s
- [x] 2.7 Implement `services.py`: `UnifiedSMSService.send(phone_number, message, category, related_user=None, related_organization=None) -> tuple[bool, str]` orchestrating: (1) URL shortening, (2) 160-char validation/truncation, (3) rate limit checks for OTP, (4) quota checks for notifications, (5) backend send, (6) SMSLog creation
- [x] 2.8 Add `SMS_ALERT_THRESHOLD` (default 140) and `SHORT_URL_DOMAIN` to settings

## 3. Fix OTP SMS Sending

- [x] 3.1 Update `users/mfa.py` `SMSAuthenticator.send_otp()`: generate OTP code AND call `UnifiedSMSService.send()` with `category=OTP`
- [x] 3.2 Update `users/views.py` `PhoneLoginView.form_valid()`: after creating OTPRequest, call `UnifiedSMSService.send()` with the OTP code as message
- [x] 3.3 Update `users/views.py` `PhoneManageView.form_valid()`: same pattern — call `UnifiedSMSService.send()` after creating OTPRequest

## 4. Migrate Notification SMSService

- [x] 4.1 Refactor `organizations/services.py` `SMSService.send()` to delegate to `UnifiedSMSService.send()` instead of directly calling MiMSMSClient
- [x] 4.2 Update `organizations/tasks.py` `send_sms_task()` to work with the refactored service (imports may change)
- [x] 4.3 Update `blood_requests/views.py` context generation to use shortened URLs for accept/decline links
- [x] 4.4 Add backward-compatibility wrapper in `organizations/services.py` that delegates to new service, with deprecation warning

## 5. Add Rate Limiting to Auth Endpoints

- [x] 5.1 Create `notifications/middleware.py`: `OTPRateLimitMiddleware` that applies IP-based rate limiting to OTP-generating paths (`/users/login/phone/`, `/users/verify/phone/`, `/users/verify/phone/otp/`)
- [x] 5.2 Add `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers to rate-limited responses
- [x] 5.3 Integrate per-phone OTP rate limit check inside `UnifiedSMSService.send()` for `category=OTP` — returns `(False, "Rate limit exceeded")` without calling provider

## 6. Update SMS Templates

- [x] 6.1 Review all SMS templates in `templates/notifications/sms/` and ensure they work with shortened URLs
- [x] 6.2 Create an OTP SMS template `templates/notifications/sms/otp_verification.txt` (message is generated in Python via `UnifiedSMSService._format_otp_message()` for brevity)
- [x] 6.3 Ensure templates are optimized to stay within ~140 chars after URL substitution

## 7. Tests & Verification

- [x] 7.1 Write unit tests for `url_shortener.py`: creation, deduplication, resolution, expiry
- [x] 7.2 Write unit tests for `rate_limiter.py`: OTP rate limit enforcement, IP rate limit enforcement, TTL behavior
- [x] 7.3 Write unit tests for `UnifiedSMSService.send()`: successful send flow, 160-char truncation, rate limit blocking, SMSLog creation
- [x] 7.4 Write unit tests for `MiMSMSBackend`: success response, failure handling
- [x] 7.5 Update existing `test_notifications.py` and `test_tasks.py` to test against new service instead of old SMSService
- [x] 7.6 Write integration test for full OTP flow: PhoneLoginView → UnifiedSMSService → SMSLog entry
- [x] 7.7 Run `just check` and ensure 95%+ coverage
