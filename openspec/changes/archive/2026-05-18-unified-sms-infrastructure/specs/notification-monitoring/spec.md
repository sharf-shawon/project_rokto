## ADDED Requirements

### Requirement: Unified SMS Audit Log View

The system SHALL provide a single `SMSLog` admin view that displays ALL outbound SMS regardless of category (OTP, EMERGENCY, INVITE, OTHER), filterable by category, status, phone number, and date range.

#### Scenario: Superuser views all SMS logs

- **WHEN** a superuser accesses the global admin SMS Log section
- **THEN** they SHALL see all SMS records across all categories (OTP, EMERGENCY, INVITE, OTHER)
- **AND** they SHALL be able to filter by category, status, phone number, and date range

#### Scenario: Org admin views org-related SMS logs

- **WHEN** an organization admin accesses the org admin SMS Log section
- **THEN** they SHALL only see SMS records where `related_organization` matches their organization
- **AND** the logs SHALL be read-only

### Requirement: SMS Message Length Monitoring

The `SMSLog` model SHALL store the message character count for every outbound SMS to enable monitoring of SMS length compliance.

#### Scenario: Message length logged

- **WHEN** an SMS is sent through the unified service
- **THEN** the `message_length` field of the `SMSLog` record SHALL contain the exact character count of the message sent
- **AND** any `TRUNCATED` status SHALL record both the original and truncated lengths

### Requirement: Truncation Alerting

The system SHALL flag SMS messages that are truncated or approach the 160-character limit for monitoring and template optimization.

#### Scenario: Truncation warning in admin

- **WHEN** an admin views the SMS Log
- **THEN** entries with `status=TRUNCATED` SHALL be visually highlighted (e.g., with a warning badge)
