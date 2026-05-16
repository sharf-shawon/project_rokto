## ADDED Requirements

### Requirement: Blood Request Creation

The system SHALL allow verified users (Seekers) to create blood requests specifying the reason, number of bags needed, donation date, and hospital location.

#### Scenario: Successful blood request creation

- **WHEN** a seeker submits a request with valid details
- **THEN** the system saves the request and triggers a donor search.

### Requirement: Donor Response Management

The system SHALL allow matched donors to respond to blood requests with ACCEPTED or DECLINED status.

#### Scenario: Donor accepts request

- **WHEN** a donor accepts a pending request
- **THEN** the request status for that donor changes to ACCEPTED and contact reveal becomes possible.

### Requirement: Dual-Party Confirmation

A donation SHALL only be considered successful when both the seeker and the donor confirm the donation (YES/YES).

#### Scenario: Successful donation confirmation

- **WHEN** both seeker and donor confirm "YES" for a request
- **THEN** the donor's `last_donation_date` is updated and the request is marked as fully confirmed.
