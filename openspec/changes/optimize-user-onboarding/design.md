## Context

Project Rokto's user onboarding currently has two parallel auth paths:

1. **django-allauth signup** (email + username + password) — requires email verification before access
2. **Phone OTP flow** (custom) — enter phone → OTP → if new user, collect name + email → auto-login

After login, `VerificationMiddleware` checks NID and phone verification. Phone-signup users get `is_phone_verified = True` at account creation, but the phone management page still shows as a required step for completeness. Email is listed as required in both `ACCOUNT_SIGNUP_FIELDS` and `UserInfoForm`, forcing users to provide an email even if they only want phone-based auth.

**Key constraints:**

- django-allauth v65.16.1 is used for email/password auth and social accounts
- Custom `PhoneOTPBackend` handles phone-based auth
- `VerificationMiddleware` gates access to most pages behind NID + phone verification
- The `User.phone_number` field supports `blank=True, null=True` (optional on the model)
- `User.email` is inherited from `AbstractUser` and already has `blank=True`

## Goals / Non-Goals

**Goals:**

- Make email completely optional across all signup/login paths
- Make email verification non-blocking ("optional" instead of "mandatory")
- Ensure phone signup users never get asked to re-verify their phone
- Present all auth options clearly on login/signup pages
- Simplify the phone signup info form to only require name
- Update all tests to reflect these changes

**Non-Goals:**

- Changing the password-based auth flow
- Modifying the NID verification system
- Adding social auth improvements (beyond what exists)
- Redesigning the overall UI layout
- Changing the VerificationMiddleware logic (only confirming it works correctly)

## Decisions

### 1. Make email optional via allauth settings

| Decision        | Detail                                                                                                                                                             |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Change**      | `ACCOUNT_SIGNUP_FIELDS` from `["email*", "username*", "password1*", "password2*"]` to `["email", "username*", "password1*", "password2*"]` (remove `*` from email) |
| **Why**         | This makes email an optional field in allauth's signup form without requiring code changes to the form itself                                                      |
| **Alternative** | Custom allauth form override to hide email — rejected because the setting natively supports this                                                                   |

### 2. Change email verification to optional

| Decision        | Detail                                                                                                                         |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Change**      | `ACCOUNT_EMAIL_VERIFICATION` from `"mandatory"` to `"optional"`                                                                |
| **Why**         | Mandatory email verification blocks users who don't have/want email. "Optional" lets users add/verify email later if they want |
| **Alternative** | `"none"` — rejected because we still want to support email as an optional verified channel for notifications                   |
| **Note**        | This is a **breaking config change** — environments relying on mandatory email verification will need to handle this           |

### 3. Make email optional in UserInfoForm

| Decision   | Detail                                                                                             |
| ---------- | -------------------------------------------------------------------------------------------------- |
| **Change** | In `UserInfoForm.Meta.fields` keep `["name", "email"]` but add `required=False` to the email field |
| **Why**    | Phone OTP signup users should only need name. Email is optional                                    |

### 4. Unified auth option links

| Decision   | Detail                                                                                                                                                                                                                  |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Change** | Update `phone_login.html` to show "Phone Sign In / Sign Up" heading. Add links to `account_signup` and `account_login` on all auth pages. Add `phone_login` link on allauth pages. Update navbar to show "Phone" option |
| **Why**    | Users should see all available auth methods, not be funneled into one path                                                                                                                                              |

### 5. Phone login page messaging

| Decision   | Detail                                                                                                                                                   |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Change** | Update heading from "Phone Login" to "Sign In / Sign Up with Phone". Add descriptive text: "Enter your phone number to sign in or create a new account." |
| **Why**    | Current "Phone Login" implies only existing users, but the flow handles both login and signup transparently                                              |

### 6. No changes to verification flow logic

| Decision   | Detail                                                                                                                                                                                                                          |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Change** | No code changes to `SignupInfoView`, `OTPVerifyView`, or `VerificationMiddleware`                                                                                                                                               |
| **Why**    | The existing flow already correctly sets `is_phone_verified = True` at signup. The middleware checks this and won't redirect. This is already working — the confusion was from the phone manage page showing as a separate step |

## Risks / Trade-offs

| Risk                                                                                  | Mitigation                                                                                                 |
| ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **Existing users with only email will no longer be forced to add phone**              | That's fine — they can add it later. The `User.phone_number` field is nullable                             |
| **Email as optional reduces notification delivery guarantees**                        | Since the primary channel is SMS (phone), this is acceptable. Email is supplemental                        |
| **ACCOUNT_EMAIL_VERIFICATION="optional" allows unverified emails to access the site** | This is intentional — phone is the primary identity mechanism. Email can be verified later                 |
| **Users may skip email entirely and lose password recovery option**                   | Password reset can use phone OTP as an alternative (future enhancement). For now, username is login method |

## Migration Plan

1. Update `config/settings/base.py` settings
2. Update `UserInfoForm` in `forms.py`
3. Update `phone_login.html` template
4. Update `signup_info.html` template
5. Update `base.html` navbar
6. Update allauth login/signup templates if present
7. Update tests

**Rollback:** Revert the settings changes and re-run migrations (no schema migrations needed — all changes are config/form/template level)

## Open Questions

- Should we also make email optional in the `UserUpdateForm` (profile update)? → It's already not directly required there, but the form inherits from `UserAdminChangeForm` in tests.
