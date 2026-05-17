## 1. Settings Configuration

- [ ] 1.1 Change `ACCOUNT_SIGNUP_FIELDS` in `config/settings/base.py` to make email optional (remove `*` from `"email*"`)
- [ ] 1.2 Change `ACCOUNT_EMAIL_VERIFICATION` from `"mandatory"` to `"optional"` in `config/settings/base.py`

## 2. Form Updates

- [ ] 2.1 Update `UserInfoForm` in `project_rokto/users/forms.py` to make email optional (add `required=False`)

## 3. Template Updates

- [ ] 3.1 Update `phone_login.html` — change heading to "Sign In / Sign Up with Phone", update description to explain dual purpose, ensure links to `account_signup` and `account_login` are present
- [ ] 3.2 Update `signup_info.html` — update the form description to clarify email is optional
- [ ] 3.3 Update `base.html` — rename "Phone Sign In" nav link to "Phone Sign In / Up" for clarity; ensure all auth options are visible

## 4. Tests

- [ ] 4.1 Update existing `test_auth.py` tests to account for optional email (e.g., signup info test without email)
- [ ] 4.2 Add test for phone signup without email (UserInfoForm submission with only name, no email)
- [ ] 4.3 Add test verifying phone login page shows links to other auth methods
- [ ] 4.4 Update any test that checks `ACCOUNT_EMAIL_VERIFICATION = "mandatory"` assumption

## 5. Verification

- [ ] 5.1 Run `just check` to ensure lint, type, and tests pass
- [ ] 5.2 Run `just test-coverage` to ensure coverage >= 95%
