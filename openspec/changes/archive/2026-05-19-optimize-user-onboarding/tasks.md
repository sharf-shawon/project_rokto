## 1. Settings & Infrastructure

- [x] 1.1 Update `config/settings/base.py` with `ACCOUNT_EMAIL_VERIFICATION = "optional"` and optional email signup fields.
- [x] 1.2 Add `allauth.socialaccount.providers.google` and `facebook` to `INSTALLED_APPS`.
- [x] 1.3 Configure `SOCIALACCOUNT_PROVIDERS` and set `SOCIALACCOUNT_EMAIL_AUTHENTICATION = True` in `base.py`.

## 2. Middleware & Forms

- [x] 2.1 Update `VerificationMiddleware` to exempt superusers and the user's own profile detail page.
- [x] 2.2 Modify `UserInfoForm` and `UserUpdateForm` in `project_rokto/users/forms.py` to make the email field optional (`required=False`).
- [x] 2.3 Verify `SignupInfoView` logic ensures `is_phone_verified=True` is set upon account creation.

## 3. Templates & UI

- [x] 3.1 Create a shared template snippet `project_rokto/templates/users/_social_auth_links.html` that dynamically lists social providers and phone/email options.
- [x] 3.2 Update `project_rokto/templates/users/phone_login.html` to include the social auth snippet and rename headings for dual-purpose (Sign In / Up).
- [x] 3.3 Create allauth overrides in `project_rokto/templates/account/login.html` and `account/signup.html` to include social and phone login links.
- [x] 3.4 Implement the \"Recovery Nudge\" card in `project_rokto/templates/users/user_detail.html` for users missing email or password.
- [x] 3.5 Update the navbar in `project_rokto/templates/base.html` for consistent \"Phone Sign In / Up\" terminology.

## 4. Verification & Testing

- [x] 4.1 Update `project_rokto/users/tests/test_auth.py` and `test_views.py` to reflect optional email requirements.
- [x] 4.2 Add test cases for `VerificationMiddleware` superuser and profile page exemptions.
- [x] 4.3 Add test cases for phone signup auto-verification and social account phone verification enforcement.
- [x] 4.4 Run `just check` to verify the 95.00% coverage requirement and ensure no regressions.
