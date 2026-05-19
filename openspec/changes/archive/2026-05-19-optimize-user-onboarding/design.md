## Context

Project Rokto's user onboarding currently splits users into two parallel paths: a custom Phone OTP flow and a standard django-allauth email/password flow. These paths are disconnected, and the system enforces mandatory email verification which blocks Bangladeshi users who primarily use phone numbers. Additionally, the `VerificationMiddleware` is overly restrictive, and there is no support for modern social authentication providers like Google or Facebook.

## Goals / Non-Goals

**Goals:**

- Unify all authentication methods (Phone, Email, Social) with clear cross-linking.
- Make email entirely optional during signup, login, and profile management.
- Allow authenticated users to view their own profile even if unverified (Safe Zone).
- Ensure superusers are never blocked by verification middleware.
- Nudge phone-only users to add an email and password for account recovery.

**Non-Goals:**

- Modifying the underlying NID verification process.
- Implementing SMS-based password recovery (out of scope for onboarding refinement).
- Redesigning the core UI branding or layout.

## Decisions

### 1. django-allauth Configuration for Optional Email

We will modify `config/settings/base.py` to set `ACCOUNT_EMAIL_VERIFICATION = "optional"` and update `ACCOUNT_SIGNUP_FIELDS` to remove the mandatory flag from `email`.

- **Rationale**: This natively supports optional email without complex form overrides.
- **Alternatives**: Customizing allauth forms manually (rejected for higher maintenance cost).

### 2. Social Authentication Integration

We will add `google` and `facebook` as social providers via `django-allauth.socialaccount`.

- **Rationale**: Leveraging a standard library for security and speed.
- **Implementation**: Providers added to `INSTALLED_APPS`, and `SOCIALACCOUNT_EMAIL_AUTHENTICATION = True` to enable automatic linking by email.

### 3. Middleware Exemption Logic

Update `VerificationMiddleware` to:

1. Return early if `request.user.is_superuser`.
2. Add `reverse("users:detail", kwargs={"username": request.user.username})` to the exempt URLs.

- **Rationale**: Prevents developers/admins from getting locked out and gives users a "safe zone" to manage their profile and add recovery options.

### 4. Unified Auth Template Strategy

Instead of hardcoding links, we will create a `_social_auth_links.html` snippet that uses `allauth`'s `{% get_providers %}` tag.

- **Rationale**: Ensures that adding a new social provider in settings automatically updates all login/signup screens.
- **Integration**: Included in `phone_login.html`, `account/login.html`, and `account/signup.html`.

### 5. Profile Nudge Component

A small alert or card in `user_detail.html` that appears only for the owner of the profile.

- **Logic**: `if request.user == object and (not object.email or not object.has_usable_password())`.
- **Rationale**: Balances "low friction" (optional email) with "user safety" (account recovery).

## Risks / Trade-offs

- **[Risk]** Account recovery: Users signing up via phone without an email might lose access if they lose their SIM card. → **Mitigation**: The Profile Nudge encourages adding email/password, and future work will implement SMS-based recovery.
- **[Risk]** Choice overload: Four login options might confuse users. → **Mitigation**: Phone remains the primary highlighted action; Social/Email are presented as secondary "Other options" in a clean grid.
