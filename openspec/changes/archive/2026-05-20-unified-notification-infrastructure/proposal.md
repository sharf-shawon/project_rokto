## Why

The current notification system is fragmented, with logging split between technical technical `SMSLog` (in the `notifications` app) and high-level `NotificationLog` (in the `organizations` app). This results in system-critical communications like OTPs being invisible in the main admin dashboard. Additionally, there is no centralized "gate" that ensures every outbound message (SMS, Email, Push) is logged with its status, making monitoring and debugging difficult.

## What Changes

- **Centralized Notification Gate** — Introduction of `UnifiedNotificationService` as the single entry point for all outbound communications.
- **Model Consolidation** — Moving `NotificationLog` from the `organizations` app to the `notifications` app to serve as a project-wide audit trail.
- **System-Wide Logging** — Every message, including OTPs and system alerts, will now create a `NotificationLog` entry.
- **Enhanced Admin Visibility** — A unified "Notification Logs" view in the Django admin that aggregates all channels (SMS, Email, WebPush).
- **Consolidated Notification Backends** — Refactoring existing email and push services to utilize the centralized logging gate.

## Capabilities

### New Capabilities

- `unified-notification-infrastructure`: A centralized dispatch and logging system for all communication channels.
- `communication-observability`: Enhanced monitoring and visibility of all outbound system messages.

### Modified Capabilities

- `unified-sms-service`: Updated to integrate with the project-wide `NotificationLog`.
- `notification-dispatcher`: Refactored to route all traffic through the new centralized gate.

## Impact

- **Models**: Move `NotificationLog` from `organizations.models` to `notifications.models`. Update `SMSLog` to potentially link to its parent `NotificationLog`.
- **Services**: New `UnifiedNotificationService`. Refactor `SMSService`, `EmailService`, and `WebPushService` to delegate to the new unified gate.
- **Views**: Update `PhoneLoginView` and others to use the enhanced logging.
- **Admin**: Consolidate notification log admins into the `notifications` app.
- **Database**: Migration to move existing logs and update foreign key relationships.
