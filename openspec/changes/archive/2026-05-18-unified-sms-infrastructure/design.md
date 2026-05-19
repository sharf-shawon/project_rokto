## Context

Project Rokto currently sends SMS through two disconnected paths:

1. **OTP/Auth SMS** — `users/mfa.py` (`SMSAuthenticator.send_otp()`), `users/views.py` (`PhoneLoginView.form_valid()`, `PhoneManageView.form_valid()`): These create OTP records but **never call any SMS provider**. The OTP is stored in the database and the user is redirected to an OTP verification page, but the SMS is never sent.

2. **Notification SMS** — `organizations/services.py` (`SMSService.send()`): This works correctly, connecting to MiMSMS via `django-mimsms`. However, it lacks 160-char enforcement, URL shortening, and its logs are limited to the `NotificationLog` model (which doesn't cover auth SMS).

The `organizations` app currently owns the SMS sending infrastructure, but this is a misplacement — SMS is a cross-cutting concern used by auth, blood requests, donor management, and organizations.

## Goals / Non-Goals

## Decisions

### Decision 1: New `notifications` app vs. extending `organizations`

**Chosen: New `notifications` app.**

Rationale:

- SMS sending is a cross-cutting concern, not an organizational feature. Auth, blood requests, and organizations all need it.
- The `organizations` app is already large (models, services, tasks, admin, tests). Adding more bloat violates single responsibility.
- A `notifications` app signals architectural intent — this is the central notification hub.
- Migration path: The existing `SMSService` class moves to `notifications/services.py`; `organizations/tasks.py` imports from the new location.

Alternatives considered:

- **Extend `organizations`**: Simpler migration but creates architectural debt. Rejected because SMS is used by `users` and `blood_requests` apps.
- **Put it in a shared `core` app**: Too vague. "Notifications" describes the domain precisely.

### Decision 2: URL shortener approach

**Chosen: Self-hosted Django model + hashids.**

Rationale:

- No external dependency on third-party URL shorteners — aligns with "sovereign network" vision
- Hashids produces short, URL-safe codes from integer IDs (6-8 chars)
- Simple model: `ShortURL(id, original_url, created_at, expires_at)`
- Short URLs can have expiry (30 days for OTP links, 7 days for donation links)
- Short URL domain configured via `SHORT_URL_DOMAIN` env var

Alternatives considered:

- **Third-party API (bit.ly, TinyURL)**: Adds latency, rate limits, external dependency. Rejected for sovereignty.
- **UUID-based short codes**: Too long (36 chars). Hashids gives 6-8 chars for millions of URLs.

### Decision 3: Rate limiting — Redis vs. DB

**Chosen: Redis for all rate limiting.**

Rationale:

- Redis is already a dependency (Celery broker, cache backend)
- Redis TTL-based expiry is perfect for rate limiting windows
- Atomic INCR + EXPIRE is cheaper than DB queries for high-frequency auth endpoints
- Already used for 24-hour donor cool-off — extending the pattern is natural

OTP rate limit key: `otp_rate_limit:{phone}` — 5 requests, 3600s TTL
IP rate limit key: `ip_rate_limit:{ip}` — 1 request, 30s TTL

### Decision 4: SMSLog model

**Chosen: New `SMSLog` model in the `notifications` app.**

Fields: `id` (UUID), `phone_number`, `message`, `message_length`, `category` (OTP, EMERGENCY, INVITE, OTHER), `provider_response` (JSON), `status` (SENT, FAILED, BLOCKED), `failure_reason`, `related_user` (FK User, nullable), `related_organization` (FK Organization, nullable), `created_at` (auto).

This replaces `NotificationLog` for SMS entries. `NotificationLog` remains for email/webpush.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                   UNIFIED SMS ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────┤
│  project_rokto/notifications/                                       │
│  ├── models.py          → SMSLog, ShortURL                         │
│  ├── services.py        → UnifiedSMSService (the single entry)     │
│  ├── backends.py        → MiMSMSBackend (provider adapter)         │
│  ├── rate_limiter.py    → Redis-based rate limiter                 │
│  ├── url_shortener.py   → ShortURL creation/resolution             │
│  ├── admin.py           → SMSLog + ShortURL admin views            │
│  └── tests/             → Full test suite                          │
│                                                                     │
│  CALLERS (updated imports):                                        │
│  ┌──────────────────────┐                                           │
│  │ users/mfa.py         │──┐                                       │
│  │ users/views.py       │──┤                                       │
│  │ organizations/tasks.py│──┤──▶ UnifiedSMSService.send()           │
│  │ blood_requests/views │  │                                       │
│  └──────────────────────┘  │                                       │
│                            │  Flow within UnifiedSMSService.send(): │
│                            │  1. Validate message length           │
│                            │  2. Shorten URLs                      │
│                            │  3. Check rate limits (if OTP)        │
│                            │  4. Check quotas (if notification)    │
│                            │  5. Send via provider                 │
│                            │  6. Log to SMSLog                     │
│                            │  7. Return success/failure            │
└─────────────────────────────────────────────────────────────────────┘
```

## Risks / Trade-offs

- **[Risk] Existing `SMSService` in `organizations` is used by multiple callers** → Keep a backward-compatibility wrapper in `organizations/services.py` that delegates to the new service, then remove after testing.
- **[Risk] URL shortener adds a DB write per SMS** → Short URLs are cached. Same full URL always produces same short code.
- **[Risk] Hashids collisions with short code length** → Use min length 6 + secret salt. 56B combinations at 6 chars.
- **[Trade-off] New `notifications` app = new migration** → Lightweight (2 models), straightforward.
- **[Trade-off] Redis rate limiter is ephemeral** → Acceptable for auth OTP abuse prevention. DB quotas are authoritative.

## Migration Plan

1. Create `notifications` app with `SMSLog` and `ShortURL` models
2. Implement `UnifiedSMSService`, `MiMSMSBackend`, `rate_limiter`, `url_shortener`
3. Update `SMSAuthenticator.send_otp()` to call `UnifiedSMSService`
4. Update `PhoneLoginView` and `PhoneManageView` to call `UnifiedSMSService`
5. Migrate `SMSService` from `organizations` to delegate to `UnifiedSMSService`
6. Add rate limiting to OTP-generating views
7. Update SMS templates to use shortened URLs
8. Add admin views for `SMSLog` and `ShortURL`
9. Run full test suite

Rollback: Each step is independently revertible.

## Open Questions

- Should `ShortURL` have an expiry cleanup job (Celery Beat)?
- Should IP rate limiter apply to OTP verification endpoint too?
- Should we log full SMS message or truncated preview (privacy)?

### Decision 5: 160-char enforcement

The unified service will: (1) generate message from template, (2) shorten all URLs, (3) if result exceeds 160 chars, log warning and truncate at last word under 160, (4) `SMS_ALERT_THRESHOLD` (default 140) warns before hitting limit.

**Goals:**

- Every outbound SMS is sent through a single, centralized service
- All OTP SMS are actually delivered (fix the bug)
- SMS payloads never exceed 160 characters (GSM 7-bit single segment)
- URLs in SMS are shortened automatically before sending
- Per-phone OTP rate limiting (max 5 OTP requests per phone per hour)
- Per-IP rate limiting on OTP-generating endpoints (max 1 request per 30s)
- Every outbound SMS is logged in a central `SMSLog` table
- Existing notification SMS continues to work with minimal friction

**Non-Goals:**

- Replacing the MiMSMS provider
- Adding email or WebPush to the unified service
- Implementing delivery receipts beyond what MiMSMS provides
- Supporting international SMS (Bangladesh-only for now)
