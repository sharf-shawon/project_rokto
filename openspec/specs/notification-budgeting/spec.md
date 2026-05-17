# notification-budgeting Specification

## Requirements

### Requirement: Global Notification Quota

The system SHALL enforce global daily and monthly limits for all notification channels (SMS, Email, WebPush) to prevent platform-wide budget overruns. These quotas SHALL be visible and editable by superusers in the global admin.

#### Scenario: Global SMS limit reached

- **WHEN** the platform attempts to send an SMS and the global daily limit has been reached
- **THEN** the system SHALL reject the request and log a quota exhaustion event.

#### Scenario: Global quota visibility

- **WHEN** a superuser views the Notification Quotas in global admin
- **THEN** they SHALL see the current usage and limits for all global channels.

### Requirement: Organization-Level Budgeting

The system SHALL allow super-admins to configure daily, weekly, and monthly notification budgets for individual organizations. These budgets SHALL be visible (read-only) to organization admins in the `org_admin_site`.

#### Scenario: Organization exceeds monthly budget

- **WHEN** an organization attempts to send an invite SMS and their monthly budget is depleted
- **THEN** the system SHALL block the notification and notify the Organization Admin.

#### Scenario: Org Admin views own quota

- **WHEN** an organization admin views their quota in the `org_admin_site`
- **THEN** they SHALL see their remaining budget and usage counters.
- **AND** they SHALL NOT be able to edit or delete the quota records.

### Requirement: User Notification Rate Limiting

The system SHALL enforce a "cooling-off" period for individual users to prevent spamming the same phone number/email repeatedly.

#### Scenario: Repeat invite protection

- **WHEN** an organization attempts to send a second invite to the same phone number within 24 hours
- **THEN** the system SHALL delay or block the notification.
