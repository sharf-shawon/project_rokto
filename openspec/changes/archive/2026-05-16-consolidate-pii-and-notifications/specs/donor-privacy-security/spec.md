## ADDED Requirements

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
