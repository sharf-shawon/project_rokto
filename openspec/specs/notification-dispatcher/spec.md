# notification-dispatcher Specification

## Requirements

### Requirement: Unified Channel Routing

The system SHALL provide a centralized dispatcher that routes notifications to SMS, Email, or Web Push based on user preferences and message priority.

#### Scenario: Routing an emergency alert

- **WHEN** a critical blood request is created
- **THEN** the dispatcher SHALL attempt delivery via SMS and Web Push simultaneously if the user has opted in.

### Requirement: Preference-Aware Dispatch

The dispatcher SHALL verify a user's `NotificationPreference` settings before initiating any channel-specific send operation.

#### Scenario: User opted out of Email

- **WHEN** the system attempts to send a non-critical update
- **AND** the user has disabled Email notifications
- **THEN** the system SHALL skip the Email channel.

### Requirement: Quota Integration

The dispatcher SHALL call the `QuotaService` to verify available budget and cool-off status before dispatching any billable notification (SMS).

#### Scenario: Quota exceeded

- **WHEN** an organization attempts to send a donor invite
- **AND** the organization's daily SMS quota is reached
- **THEN** the dispatcher SHALL block the SMS and log the failure.

### Requirement: Reliable Scheduler Initialization

The system SHALL ensure that the Celery Beat scheduler service only starts after all database migrations, specifically those for `django_celery_beat`, have been successfully applied.

#### Scenario: Startup with pending migrations

- **WHEN** the docker-compose environment is starting
- **AND** the `django_celery_beat` tables are not yet present in the database
- **THEN** the `celerybeat` service SHALL wait for the migration process to complete before attempting to initialize the scheduler.
