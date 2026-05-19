## MODIFIED Requirements

### Requirement: Unified Channel Routing

The system SHALL provide a centralized dispatcher that routes notifications to SMS, Email, or Web Push based on user preferences and message priority.

#### Scenario: Routing an emergency alert

- **WHEN** a critical blood request is created
- **THEN** the dispatcher SHALL attempt delivery via SMS and Web Push simultaneously if the user has opted in.
- **AND** the SMS dispatch SHALL route through `UnifiedSMSService` which performs 160-char enforcement and URL shortening before sending.

### Requirement: Quota Integration

The dispatcher SHALL call the `QuotaService` to verify available budget and cool-off status before dispatching any billable notification (SMS).

#### Scenario: Quota exceeded

- **WHEN** an organization attempts to send a donor invite
- **AND** the organization's daily SMS quota is reached
- **THEN** the dispatcher SHALL block the SMS and log the failure.

## ADDED Requirements

### Requirement: 160-Character Enforcement in SMS Dispatch

The notification dispatcher SHALL ensure that SMS messages dispatched through it comply with the 160-character single-segment limit.

#### Scenario: Truncated emergency SMS

- **WHEN** an emergency SMS message exceeds 160 characters after URL shortening
- **THEN** the dispatcher SHALL truncate the message at the last complete word under 160 characters
- **AND** log a warning entry in `SMSLog`

### Requirement: URL Shortening Before SMS Dispatch

The notification dispatcher SHALL automatically shorten all URLs in SMS message templates before sending.

#### Scenario: URLs shortened in donor invite

- **WHEN** a donor invite SMS is queued for sending
- **THEN** the invite URL in the message SHALL be replaced with a shortened URL from the `url-shortener` service
