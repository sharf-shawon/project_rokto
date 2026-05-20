## ADDED Requirements

### Requirement: Centralized Notification Dispatch

The system SHALL provide a unified entry point, `UnifiedNotificationService.send()`, for all outbound communications across all channels (SMS, Email, WebPush).

#### Scenario: Dispatching an SMS

- **WHEN** a system component calls `UnifiedNotificationService.send()` with an SMS payload
- **THEN** the system SHALL route the request through the SMS-specific logic and log the outcome

### Requirement: Universal Audit Logging

The system SHALL create a `NotificationLog` entry for every outbound message, regardless of its source (e.g., OTP, emergency request, donor invite) or channel.

#### Scenario: Logging a login OTP

- **WHEN** a user requests a phone login OTP
- **THEN** the system SHALL create a `NotificationLog` entry with `channel=SMS` and `category=OTP`, visible in the main admin dashboard

### Requirement: Comprehensive Status Tracking

The system SHALL record the final status (SENT, FAILED, BLOCKED) and any failure reasons for every notification attempt in the `NotificationLog`.

#### Scenario: Tracking a failed SMS

- **WHEN** an SMS dispatch fails due to a provider error
- **THEN** the corresponding `NotificationLog` SHALL have its status set to `FAILED` and include the provider's error message in `failure_reason`
