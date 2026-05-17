## Context

Currently, `Donor` records are isolated by a single `ForeignKey` to an `Organization`. PII is duplicated across `User` and `Donor`. There is no system to control notification costs or prevent spam.

## Goals / Non-Goals

**Goals:**

- Centralize PII: `phone_number` should be the unique key across the platform.
- Multi-Org Support: A donor can be managed by multiple organizations.
- Budgeting: Prevent any single org or the whole project from exceeding notification budgets.
- Auto-Linking: Transition "Guest" donors to "Verified Users" seamlessly.

**Non-Goals:**

- Implementing the actual SMS Gateway (we will use a service interface).
- Complex financial accounting (simple budget tracking is enough).

## Decisions

### 1. Unified Donor Identity (M2M)

- **Decision**: `Donor` model will use `ManyToManyField` for `organizations`.
- **Rationale**: Reflects real-world donation patterns. Prevents data silos.
- **Merge Logic**: When an org uploads a CSV, we look up `Donor` by `phone_number`. If it exists, we just add the new `Organization` to the M2M set.

### 2. The Quota Service

- **Decision**: Use a Redis-backed counter for real-time rate limiting, synchronized to a PostgreSQL `NotificationQuota` model for persistent budgeting.
- **Rationale**: Redis is fast for high-volume notification checks. PostgreSQL ensures data integrity for financial/budgetary tracking.

### 3. Identity "Promotion" Flow

- **Decision**: When a `User` signs up, a post-save signal or a specialized signup service will search for a `Donor` record with the matching `phone_number`. If found, `donor.user` is updated.
- **Rationale**: Ensures the history (previous donations, org memberships) is preserved.

## Risks / Trade-offs

- **[Risk] Privacy Leakage** → If Org A uploads PII for a donor, and Org B uploads the same phone number, they both now "see" the same donor.
  - **Mitigation**: Orgs can only see the data _they_ uploaded until the user verifies their profile and grants permissions. We will implement "Field-Level Sovereignty" where Orgs only see their own version of "Guest" data.
- **[Risk] Cost of SMS** → Massive CSV uploads triggering thousands of SMS.
  - **Mitigation**: Default "Invite" status to `PENDING_APPROVAL`. Admins must manually trigger "Send Invites" for batches, or we strictly enforce the daily Org Quota.
