## Why

The test suite is experiencing intermittent `IntegrityError` failures during database insertion, specifically in `test_confirm_donation_unauthorized_user`. This is caused by `UserFactory` using `Faker` to generate unique fields like `username` and `phone_number`, which leads to collisions when multiple users are created in quick succession.

## What Changes

- Refactor `UserFactory` in `project_rokto/users/tests/factories.py` to use `factory.Sequence` for `username`, `email`, and `phone_number` to guarantee uniqueness across all tests.
- Update imports in `factories.py` to include the `factory` module.

## Capabilities

### New Capabilities

- `test-infrastructure`: Reliable test data generation using factories.

### Modified Capabilities

- None (This is a test infrastructure fix, no functional requirements are changing)

## Impact

- **Test Infrastructure**: More reliable test runs with zero risk of unique constraint collisions in `User` creation.
- **Files**: `project_rokto/users/tests/factories.py`
