## ADDED Requirements

### Requirement: Centralized SMS Sending

The system SHALL provide a single, unified entry point for sending all SMS messages, regardless of their origin (auth OTP, blood request notifications, donor invitations). All SMS send operations SHALL pass through `UnifiedSMSService.send()`.

#### Scenario: Unified service handles OTP SMS

- **WHEN** a user requests a phone login OTP
- **THEN** `UnifiedSMSService.send()` SHALL be called with the OTP message and `category=OTP`

#### Scenario: Unified service handles emergency SMS

- **WHEN** a blood request is created and notification SMS must be sent
- **THEN** `UnifiedSMSService.send()` SHALL be called with the emergency message and `category=EMERGENCY`

### Requirement: 160-Character Enforcement

The system SHALL ensure every SMS message sent through the unified service complies with the GSM 7-bit single-segment limit of 160 characters. Messages exceeding this limit SHALL be truncated at the last complete word boundary under 160 characters.

#### Scenario: Message under 160 characters

- **WHEN** the rendered SMS template produces a message of 140 characters
- **THEN** the message SHALL be sent as-is without truncation

#### Scenario: Message exceeds 160 characters after URL shortening

- **WHEN** the rendered SMS template produces a message of 200 characters after URL shortening
- **THEN** the message SHALL be truncated to the last complete word under 160 characters
- **AND** a warning SHALL be logged to `SMSLog` with `status=TRUNCATED`

#### Scenario: Alert threshold warning

- **WHEN** a message exceeds `SMS_ALERT_THRESHOLD` (default 140 characters)
- **AND** the message is under 160 characters
- **THEN** a warning SHALL still be logged to aid monitoring

### Requirement: Provider Abstraction

The unified service SHALL use a pluggable backend pattern so the SMS provider can be swapped without changing business logic.

#### Scenario: Backend interface

- **WHEN** the unified service needs to send an SMS
- **THEN** it SHALL call the configured backend's `send(phone_number, message)` method
- **AND** the backend SHALL return a standardized response with status and optional transaction ID

### Requirement: Centralized SMS Audit Logging

Every SMS sent through the unified service SHALL be recorded in `SMSLog` with full audit information.

#### Scenario: Successful SMS logged

- **WHEN** an SMS is successfully sent
- **THEN** an `SMSLog` record SHALL be created with phone_number, message, message_length, category, status=SENT, and provider_response

#### Scenario: Failed SMS logged

- **WHEN** an SMS send fails
- **THEN** an `SMSLog` record SHALL be created with status=FAILED and failure_reason containing the error details
