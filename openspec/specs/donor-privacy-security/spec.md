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

The system SHALL allow non-authenticated responses (e.g., from email links) only via a secure, unique, and non-guessable UUID token.

#### Scenario: Donor responds via email link

- **WHEN** a donor visits a URL with a valid `token`
- **THEN** they can accept or decline the request without a full login session.
