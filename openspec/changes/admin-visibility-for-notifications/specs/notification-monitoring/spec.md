## ADDED Requirements

### Requirement: Admin Access to Communication Logs

The system SHALL provide an administrative interface to view all notification logs, including channel, status, and failure reasons.

#### Scenario: Superuser views logs

- **WHEN** a superuser accesses the global admin dashboard
- **THEN** they SHALL be able to view and filter logs from all organizations.

### Requirement: Organizational Log Visibility

The system SHALL allow organization admins to view logs specifically for their organization.

#### Scenario: Org Admin views logs

- **WHEN** an organization admin accesses the `org_admin_site`
- **THEN** they SHALL only see logs for donors and alerts associated with their specific organization.
- **AND** the logs SHALL be read-only.
