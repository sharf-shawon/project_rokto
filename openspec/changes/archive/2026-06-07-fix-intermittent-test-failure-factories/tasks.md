## 1. Refactor UserFactory

- [x] 1.1 Add `import factory` to `project_rokto/users/tests/factories.py`
- [x] 1.2 Update `UserFactory` to use `factory.Sequence` for `username`
- [x] 1.3 Update `UserFactory` to use `factory.Sequence` for `email`
- [x] 1.4 Update `UserFactory` to use `factory.Sequence` for `phone_number`

## 2. Verification

- [x] 2.1 Run `just test project_rokto/blood_requests/tests/test_confirm_donation_unauthorized_user`
- [x] 2.2 Run all tests in `project_rokto/blood_requests/tests/test_coverage_gap.py`
- [x] 2.3 Run `just check` to ensure total project health
