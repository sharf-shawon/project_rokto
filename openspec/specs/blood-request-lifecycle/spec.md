# blood-request-lifecycle Specification

## Purpose

TBD - created by archiving change onboard-repo. Update Purpose after archive.

## Requirements

### Requirement: Blood Request Creation

The system SHALL allow verified users (Seekers) to create blood requests specifying the reason, number of bags needed, donation date, and hospital location. Creating a request MUST trigger automated multi-channel notifications (SMS, Email, Web Push) to matched eligible donors.

#### Scenario: Successful blood request creation

- **WHEN** a seeker submits a request with valid details
- **THEN** the system saves the request, triggers a donor search, and queues notification tasks for matched donors via the Dispatcher.

### Requirement: Donor Response Management

The system SHALL allow matched donors to respond to blood requests with ACCEPTED or DECLINED status.

#### Scenario: Donor accepts request

- **WHEN** a donor accepts a pending request
- **THEN** the request status for that donor changes to ACCEPTED and contact reveal becomes possible.

### Requirement: Dual-Party Confirmation

A donation SHALL only be considered successful when both the seeker and the donor confirm the donation (YES/YES). This confirmation logic MUST be enforced at the model level to ensure consistency across all access methods (API, Web UI, etc.).

#### Scenario: Successful donation confirmation update

- **WHEN** both seeker and donor confirm "YES" for a request
- **THEN** the donor's `last_donation_date` is updated to the request's donation date, and the request is marked as fully confirmed.

#### Scenario: Out-of-order confirmation date protection

- **WHEN** a donation is confirmed for a date that is older than the donor's existing `last_donation_date`
- **THEN** the donation is marked as confirmed, but the donor's `last_donation_date` remains unchanged.
