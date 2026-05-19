## Why

User onboarding in Project Rokto currently has friction points that reduce conversion, specifically mandatory email verification for a service primarily targeting Bangladeshi users who prefer phone-based authentication. The current parallel auth paths (Email vs. Phone) are disconnected, and users who sign up via phone are often blocked by middleware or missing recovery options. We need to unify these paths, make email optional, and add modern social login options.

## What Changes

- **Optional Email** — `ACCOUNT_EMAIL_VERIFICATION` changed to `"optional"`. Email field is removed from required signup fields and made optional in all forms.
- **Phone Signup Auto-verification** — Users signing up via Phone OTP are marked as `is_phone_verified=True` immediately, skipping redundant verification steps.
- **Social Login Integration** — Google and Facebook authentication via `django-allauth.socialaccount`.
- **Unified Auth UI** — All login/signup pages dynamically show all available methods (Phone, Email, Google, Facebook).
- **Middleware Refinement** — `VerificationMiddleware` now exempts superusers and the user profile page to prevent lockout and allow account management.
- **Recovery Nudge** — A "nudge" UI on the profile page for users without email/password to improve account recovery.

## Capabilities

### New Capabilities

- `user-onboarding-optimization`: Unified, low-friction auth flow with optional email and phone auto-verification.
- `social-auth-integration`: Integration of Google and Facebook social providers into the auth ecosystem.

### Modified Capabilities

- _(None - existing specs don't cover auth flows)_

## Impact

- **Settings**: `config/settings/base.py` for allauth and social provider configuration.
- **Forms**: `project_rokto/users/forms.py` (UserInfoForm, UserUpdateForm).
- **Middleware**: `project_rokto/users/middleware.py` (exemption logic).
- **Views**: `project_rokto/users/views.py` (login/signup flow adjustments).
- **Templates**: Navbar (`base.html`), Allauth overrides (`account/*.html`), Profile (`users/user_detail.html`).
- **Dependencies**: Add `django-allauth` social providers.
