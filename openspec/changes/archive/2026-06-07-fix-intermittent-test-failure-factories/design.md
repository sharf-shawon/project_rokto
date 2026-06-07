## Context

The `User` model requires unique `username` and `phone_number`. The `UserFactory` currently uses `Faker` which produces semi-random values that can collide, causing `IntegrityError` during `INSERT` operations in tests.

## Goals / Non-Goals

**Goals:**

- Ensure `UserFactory` always produces unique values for `username`, `email`, and `phone_number`.
- Eliminate intermittent `IntegrityError` failures in the test suite.

**Non-Goals:**

- Modifying the `User` model or any business logic.
- Changing how `Faker` is used for non-unique fields like `name`.

## Decisions

### 1. Use `factory.Sequence` for Unique Fields

- **Rationale**: `factory.Sequence` provides a deterministic way to generate unique values (e.g., `user0`, `user1`, etc.) which avoids the probabilistic collision risk of `Faker`.
- **Alternatives**: Using `Faker` with `unique=True`. _Rejected_ because it can still fail if the pool of unique values is exhausted or due to internal Faker state resets across tests. Sequences are more robust for database primary/unique keys.

### 2. Format `phone_number` as 11 digits

- **Rationale**: Bangladeshi phone numbers are typically 11 digits. Using `017{n:08d}` ensures we have a valid-looking 11-digit number starting with `017` that is unique for up to 100 million users.

## Risks / Trade-offs

- **[Risk]** Deterministic data might hide issues that only appear with certain random strings. → **Mitigation**: Only unique identifiers are made deterministic; fields like `name` still use `Faker`.
