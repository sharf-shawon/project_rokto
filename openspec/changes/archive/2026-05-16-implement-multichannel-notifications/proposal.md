## Why

Project Rokto aims to eliminate the chaos of emergency blood searches by providing automated, real-time alerts to eligible donors. Currently, the project lacks a centralized, scalable, and multi-channel notification engine to deliver these life-saving alerts via Email, SMS, and Web Push. Implementing this system is foundational to achieving the vision of a resilient and automated blood donation network.

## What Changes

- **Core Notification Engine**: A centralized service ("The Rokto Dispatcher") powered by Celery and Redis for asynchronous, multi-channel delivery.
- **SMS Integration**: Integration of the `django-mimsms` package for localized SMS delivery in Bangladesh.
- **Email Standard**: Implementation of standardized Django Mail with HTML/Plain-text dual-rendering templates.
- **Web Push**: Implementation of a browser-based Push API using `pywebpush` to ensure BDIX resilience.
- **User Sovereignty**: A new `NotificationPreference` model allowing donors to opt-in/out of specific channels for different alert types.
- **Quota & Misuse Protection**: Integration with existing Quota models to enforce organization budgets and donor "cooling-off" periods.

## Capabilities

### New Capabilities

- `notification-dispatcher`: The core engine for routing and sending multi-channel alerts.
- `web-push-resilience`: Browser-based push notification capability for local network resilience.

### Modified Capabilities

- `blood-request-lifecycle`: Update to include automated multi-channel alerts upon request creation.
- `donor-privacy-security`: Ensure contact reveals and invites are handled securely via the new engine.

## Impact

- **Services**: New `NotificationDispatcher` and `PreferenceService`.
- **Infrastructure**: New Celery workers and Redis queues for notification tasks.
- **Database**: New `NotificationPreference` model; updates to `Donor` for subscription tracking.
- **Templates**: Centralized notification templates in `templates/notifications/`.
