## Why

Project Rokto's SMS infrastructure is fragmented and broken. OTP SMS (used for login, signup, and phone verification) is **never actually sent** — the code generates an OTP, stores it in the database, and then silently returns without calling any SMS provider. This means **no user can currently log in or sign up** via phone. Additionally, notification SMS (emergency requests, donor invites) lacks 160-character validation, URL shortening for links, per-phone rate limiting, and centralized audit logging. SMS costs money and every character counts — we need a disciplined, auditable, rate-limited system.

## What Changes

- **Fix the OTP bug**: Route all OTP SMS through a unified SMS service so OTPs are actually delivered
- **Create a new `notifications` app** as the single, authoritative SMS/notification service (migrate existing `SMSService` from `organizations`)
- **Enforce 160-character limit** on all outbound SMS with truncation warnings
- **Build a self-hosted URL shortener** using Django models + hashids to compress links before sending them in SMS
- **Add per-phone OTP rate limiting** (5 requests/hour) and per-IP rate limiting (1 request/30s) on auth endpoints
- **Centralize SMS logging** with a new `SMSLog` model recording every outbound SMS regardless of origin
- **Update existing callers**: `SMSAuthenticator`, `PhoneLoginView`, `PhoneManageView`, and `SMSService` all use the new unified service

## Capabilities

### New Capabilities

- `unified-sms-service`: Central SMS sending service with provider abstraction, 160-char enforcement, URL shortening, and full audit logging
- `url-shortener`: Self-hosted URL shortening using Django models + hashids for SMS link compression
- `sms-rate-limiting`: Redis-based rate limiting per phone number (OTP) and per IP address (auth endpoints)

### Modified Capabilities

- `notification-dispatcher`: `SMSService` moves from `organizations` app to new `notifications` app; add 160-char enforcement and URL shortening before dispatch
- `notification-budgeting`: Extend existing quota/cool-off checks with per-phone OTP rate limits (shorter expiry, higher frequency)
- `notification-monitoring`: `SMSLog` model extends logging beyond notifications to include auth-OTP SMS; admin views show all SMS across categories

## Impact

- **New app**: `project_rokto/notifications/` — the new unified notification hub
- **New models**: `SMSLog` (central audit log), `ShortURL` (URL shortening)
- **New package**: `django-hashids` (for URL short codes)
- **Modified apps**: `users` (OTP paths call new service), `organizations` (SMSService migrated), `blood_requests` (URL shortening in SMS context)
- **New Redis keys**: Rate limiting keys for per-phone and per-IP
- **Environment**: Add `SHORT_URL_DOMAIN` (e.g., `rkto.gg`) to `.envs`
- **No breaking API changes** — internal refactoring only
