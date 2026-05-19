## ADDED Requirements

### Requirement: Individual Verification Status Badges

The system SHALL display separate verification statuses for Phone Number, National ID (NID), and Email on the user profile page.

#### Scenario: Viewing verification statuses

- **WHEN** a user views a profile page
- **THEN** they SHALL see individual badges or indicators for "Phone", "NID", and "Email" verification states

### Requirement: Direct Verification Action Links

The system SHALL provide direct links to the relevant verification flow for any unverified requirements on the user's own profile.

#### Scenario: User has unverified NID

- **WHEN** a user views their own profile and their NID is not verified
- **THEN** the "NID" status badge SHALL include a "Verify Now" link directed to the NID submission page

### Requirement: Dynamic Verification Messaging

The system SHALL display clear, concise messages explaining what each verification status means (e.g., "Verified", "Pending Review", "Not Provided").

#### Scenario: User has pending NID verification

- **WHEN** a user's NID submission is currently being reviewed
- **THEN** the NID status indicator SHALL display "Pending Review" in an appropriate informational style (e.g., blue badge)
