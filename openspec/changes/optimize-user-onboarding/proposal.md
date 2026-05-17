## Why

User onboarding in Project Rokto has unnecessary friction points that reduce sign-up conversion. Email is required and mandatory to verify, but the app's core mission — blood donation in Bangladesh — works entirely via phone number. Users who sign up via the phone OTP flow must re-verify their phone again later (via the VerificationMiddleware/phone_manage flow). The two auth paths (allauth email signup vs phone login/signup) are disconnected with poor cross-referencing. These issues create drop-off in the critical first-time user experience.

## What Changes

1. **Make email optional** — `ACCOUNT_SIGNUP_FIELDS` removes `email*` requirement. `ACCOUNT_EMAIL_VERIFICATION` changes from `"mandatory"` to `"optional"`. The `UserInfoForm` makes email not required.
2. **Phone number flow auto-verification** — When a new user signs up via phone OTP, `is_phone_verified = True` is set at creation time, and the VerificationMiddleware will not redirect them to re-verify.
3. **Unify auth option visibility** — The phone login page, allauth login page, and allauth signup page all show links to the other available auth methods. The navbar shows both "Phone Sign In/Up" and "Email Sign In/Up".
4. **Improve `phone_login.html` messaging** — Rename/label to communicate it handles both sign in AND sign up.
5. **Simplify signup info form** — Only `name` is required; `email` is optional.
6. **Ensure no duplicate phone verification** — The `SignupInfoView` already sets `is_phone_verified = True`, but we confirm the middleware doesn't re-route back to phone verification.

## Capabilities

### New Capabilities

- `phone-auth-flow`: Phone number based authentication (OTP login + signup unified)
- `email-as-optional`: Email is entirely optional across the auth system — signup, login, and profile

### Modified Capabilities

- _(None — existing specs don't cover user auth/onboarding directly)_

## Impact

- **`config/settings/base.py`**: `ACCOUNT_SIGNUP_FIELDS`, `ACCOUNT_EMAIL_VERIFICATION` changes
- **`project_rokto/users/forms.py`**: `UserInfoForm` — make email optional
- **`project_rokto/users/views.py`**: Minor adjustments to flow clarity
- **`project_rokto/users/templates/users/`**: Update phone_login, signup_info templates for better UX and cross-linking
- **`project_rokto/templates/base.html`**: Update navbar auth links
- **Tests**: Update existing tests, add new tests for optional email, phone-only flow
