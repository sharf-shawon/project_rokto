## ADDED Requirements

### Requirement: Unified Admin Monitoring Dashboard

The system SHALL provide a centralized "Notification Logs" view in the Django Admin that displays all outbound communications across all channels.

#### Scenario: Admin views recent communications

- **WHEN** an admin navigates to the "Notification Logs" section in the admin panel
- **THEN** they SHALL see a sortable and filterable list of all messages (SMS, Email, WebPush) from all parts of the system

### Requirement: Cross-Channel Visibility

The system SHALL allow admins to filter notification logs by channel, status, and related organization to monitor system health and donor engagement.

#### Scenario: Admin filters by failed SMS

- **WHEN** an admin applies a filter for `channel=SMS` and `status=FAILED`
- **THEN** the system SHALL display only the failed SMS records, allowing for quick troubleshooting of provider issues
