## MODIFIED Requirements

### Requirement: Blood Request Creation

The system SHALL allow verified users (Seekers) to create blood requests specifying the reason, number of bags needed, donation date, and hospital location. Creating a request MUST trigger automated multi-channel notifications (SMS, Email, Web Push) to matched eligible donors.

#### Scenario: Successful blood request creation

- **WHEN** a seeker submits a request with valid details
- **THEN** the system saves the request, triggers a donor search, and queues notification tasks for matched donors via the Dispatcher.
