## ADDED Requirements

### Requirement: Per-Phone OTP Rate Budgeting

In addition to existing global and organization-level quotas, the system SHALL enforce per-phone-number OTP rate limits as a budget control mechanism to prevent SMS spend abuse.

#### Scenario: OTP rate limit blocks excess sends

- **WHEN** a phone number exceeds 5 OTP requests in a rolling hour
- **THEN** the unified SMS service SHALL reject the request
- **AND** log the block to `SMSLog` with `category=OTP` and `status=BLOCKED`

### Requirement: L1 → L2 Budget Escalation

When per-phone OTP rate limiting blocks a legitimate user, the system SHALL fall back to the existing organization-level or global quota check for notification-type SMS.

#### Scenario: Blocked OTP does not affect notifications

- **WHEN** a phone number is rate-limited for OTP
- **AND** an emergency notification needs to be sent to the same number
- **THEN** the emergency notification SHALL still be evaluated against the existing global/organization quotas independently
