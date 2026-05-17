## MODIFIED Requirements

### Requirement: Global Notification Quota

The system SHALL enforce global daily and monthly limits for all notification channels (SMS, Email, WebPush) to prevent platform-wide budget overruns. These quotas SHALL be visible and editable by superusers in the global admin.

#### Scenario: Global quota visibility

- **WHEN** a superuser views the Notification Quotas in global admin
- **THEN** they SHALL see the current usage and limits for all global channels.

### Requirement: Organization-Level Budgeting

The system SHALL allow super-admins to configure daily, weekly, and monthly notification budgets for individual organizations. These budgets SHALL be visible (read-only) to organization admins in the `org_admin_site`.

#### Scenario: Org Admin views own quota

- **WHEN** an organization admin views their quota in the `org_admin_site`
- **THEN** they SHALL see their remaining budget and usage counters.
- **AND** they SHALL NOT be able to edit or delete the quota records.
