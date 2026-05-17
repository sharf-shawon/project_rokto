## ADDED Requirements

### Requirement: Browser-Based Push

The system SHALL implement the W3C Push API using the VAPID (Voluntary Application Server Identification) protocol.

#### Scenario: User subscribes to push

- **WHEN** a user grants permission for notifications in their browser
- **THEN** the system SHALL store their endpoint and public keys securely in the database.

### Requirement: Service Worker Lifecycle

The system SHALL provide a Service Worker capable of handling push events even when the browser tab is closed.

#### Scenario: Push event received

- **WHEN** the browser receives a push event from the VAPID server
- **THEN** the Service Worker SHALL display a rich notification with the Project Rokto logo.
