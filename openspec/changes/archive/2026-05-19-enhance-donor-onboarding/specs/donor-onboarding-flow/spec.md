## ADDED Requirements

### Requirement: Dedicated Donor Registration Flow

The system SHALL provide a distinct multi-step form for guest users to register as blood donors, separate from the standard profile update form.

#### Scenario: Guest user initiates donor registration

- **WHEN** a guest user clicks the "Become a Donor" button
- **THEN** they SHALL be directed to a form containing fields for Blood Group, Date of Birth, and Preferred Locations

### Requirement: Mandatory Donor Fields

The system SHALL enforce that Blood Group, Date of Birth, and Preferred Locations are mandatory when a user is registering as a donor.

#### Scenario: Submitting donor registration without mandatory fields

- **WHEN** a user attempts to submit the donor registration form with an empty Blood Group or Date of Birth
- **THEN** the system SHALL display validation errors and prevent form submission

### Requirement: Sectioned Form Layout

The system SHALL organize profile and donor forms into logical sections (e.g., Basic Info, Donor Details, Health Info) with clear headings.

#### Scenario: Viewing the donor registration form

- **WHEN** a user views the donor registration form
- **THEN** they SHALL see fields grouped under "Donor Information" and "Health & Availability" sections

### Requirement: Become a Donor Nudge

The system SHALL display a prominent call-to-action on the profile page for users who have not yet registered as blood donors.

#### Scenario: Guest user views their own profile

- **WHEN** a user without a donor profile views their own profile page
- **THEN** the system SHALL display a "Become a Blood Donor" card with a link to the registration flow
