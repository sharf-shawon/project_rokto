## MODIFIED Requirements

### Requirement: Centralized SMS Sending

The system SHALL provide a single, unified entry point for sending all SMS messages, regardless of their origin (auth OTP, blood request notifications, donor invitations). All SMS send operations SHALL pass through `UnifiedNotificationService.send()` (acting as the SMS handler).

#### Scenario: Unified service handles OTP SMS

- **WHEN** a user requests a phone login OTP
- **THEN** `UnifiedNotificationService.send()` SHALL be called with the OTP message and `channel=SMS`

#### Scenario: Unified service handles emergency SMS

- **WHEN** a blood request is created and notification SMS must be sent
- **THEN** `UnifiedNotificationService.send()` SHALL be called with the emergency message and `channel=SMS`

### Requirement: Centralized SMS Audit Logging

Every SMS sent through the unified service SHALL be recorded in both `NotificationLog` (high-level) and `SMSLog` (technical detail).

#### Scenario: Successful SMS logged

- **WHEN** an SMS is successfully sent
- **THEN** a `NotificationLog` record SHALL be created with `status=SENT`
- **AND** an `SMSLog` record SHALL be created with phone_number, message, status=SENT, and provider_response

#### Scenario: Failed SMS logged

- **WHEN** an SMS send fails
- **THEN** a `NotificationLog` record SHALL be created with `status=FAILED`
- **AND** an `SMSLog` record SHALL be created with status=FAILED and failure_reason containing the error details
