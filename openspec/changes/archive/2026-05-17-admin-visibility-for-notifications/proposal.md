## Why

Currently, there is no administrative interface for superusers or organization admins to monitor the health and volume of notifications. While the system correctly logs notification attempts and enforces quotas, these records are hidden, making it impossible to diagnose delivery failures, track budget usage, or audit communication with donors.

## What Changes

- **Global Admin Integration**: Register `NotificationLog` and `NotificationQuota` in the main Unfold admin site for superusers.
- **Organization Admin Integration**: Register `NotificationLog` and `NotificationQuota` in the `org_admin_site` for organization admins/managers.
- **Sidebar Navigation**: Add a new "Communications" section to the Organization Admin sidebar for easy access to logs and quotas.
- **Monitoring Tools**: Implement filters (status, channel, organization) and search (donor phone number) to handle high-volume log analysis.
- **Security**: Ensure that Organization Admins have read-only access to their own logs and quotas to prevent unauthorized modifications.

## Capabilities

### New Capabilities

- `notification-monitoring`: Interface for auditing and monitoring all outgoing communications.

### Modified Capabilities

- `notification-budgeting`: Update requirements to include administrative visibility of quotas and usage.

## Impact

- **Admin Interface**: Changes to `project_rokto/organizations/admin.py`.
- **User Experience**: Org admins gain a dashboard to monitor invite status and SMS budget.
- **Observability**: Superusers gain the ability to troubleshoot platform-wide delivery issues.
