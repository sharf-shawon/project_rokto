## MODIFIED Requirements

### Requirement: Unified Channel Routing

The system SHALL provide a centralized dispatcher that routes notifications to SMS, Email, or Web Push based on user preferences and message priority.

#### Scenario: Routing an emergency alert

- **WHEN** a critical blood request is created
- **THEN** the dispatcher SHALL attempt delivery via SMS and Web Push simultaneously if the user has opted in.
- **AND** the dispatch SHALL route through `UnifiedNotificationService` to ensure centralized logging and auditing.

### Requirement: Quota Integration

The dispatcher SHALL call the `QuotaService` to verify available budget and cool-off status before dispatching any billable notification (SMS).

#### Scenario: Quota exceeded

- **WHEN** an organization attempts to send a donor invite
- **AND** the organization's daily SMS quota is reached
- **THEN** the dispatcher SHALL block the SMS and log the failure via `UnifiedNotificationService.log_failure()`.
