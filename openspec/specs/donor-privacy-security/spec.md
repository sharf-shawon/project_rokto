# donor-privacy-security Specification

## Purpose

TBD - created by archiving change onboard-repo. Update Purpose after archive.

## Requirements

### Requirement: Conditional Contact Reveal

The system SHALL NOT reveal the phone number of a donor or seeker until the donor has ACCEPTED the blood request.

#### Scenario: Seeker attempts to see donor contact

- **WHEN** a seeker requests the donor's contact for a "PENDING" request
- **THEN** the system denies access and returns an error.

### Requirement: Contact Access Logging

The system SHALL log the timestamp when a seeker or donor first accesses the other party's contact information.

#### Scenario: Donor views seeker contact

- **WHEN** a donor clicks "Reveal Seeker Contact" for an "ACCEPTED" request
- **THEN** the system returns the number and records the current timestamp in `seeker_contact_accessed_at`.

### Requirement: Secure Token Access

The system SHALL allow non-authenticated responses (e.g., from email links) and organization invitations only via a secure, unique, and non-guessable UUID token. These links MUST be delivered via the centralized Notification Dispatcher to ensure auditability.

#### Scenario: Donor responds via email link

- **WHEN** a donor visits a URL with a valid `token`
- **THEN** they can accept or decline the request without a full login session, and the action is logged by the dispatcher.

### Requirement: PII Sovereignty for Guest Records

The system SHALL ensure that an organization can only access the "Guest" PII (name, phone) that it specifically uploaded, even if the same donor exists in other organizations, until the donor verifies their profile.

#### Scenario: Isolated guest data access

- **WHEN** "Org A" and "Org B" have the same phone number in their database as a "Guest"
- **AND** "Org A" updates the guest's name to "John Doe"
- **THEN** "Org B" SHALL NOT see the name update from "Org A".

### Requirement: Unified PII Identity

The system SHALL treat the verified `User` profile as the global source of truth for PII (name, phone, blood group) once a donor account is linked to a user.

#### Scenario: Verified data override

- **WHEN** a user verifies their account and updates their blood group to "O-"
- **THEN** all organizations associated with that donor SHALL see the verified "O-" status instead of their previously uploaded data.
