## MODIFIED Requirements

### Requirement: Secure Token Access

The system SHALL allow non-authenticated responses (e.g., from email links) and organization invitations only via a secure, unique, and non-guessable UUID token. These links MUST be delivered via the centralized Notification Dispatcher to ensure auditability.

#### Scenario: Donor responds via email link

- **WHEN** a donor visits a URL with a valid `token`
- **THEN** they can accept or decline the request without a full login session, and the action is logged by the dispatcher.
