# organization-donor-management Specification

## Requirements

### Requirement: Bulk Donor Import

The system SHALL allow Organization Admins to upload a CSV file containing donor names, phone numbers, and blood groups.

#### Scenario: Successful bulk upload

- **WHEN** an admin uploads a valid CSV with 100 donor records
- **THEN** the system SHALL create "Guest" donor records for new numbers and associate existing records with the organization.

### Requirement: Automatic Identity Linking

The system SHALL automatically link a "Guest" donor record to a "Verified User" account when a user signs up with the matching phone number.

#### Scenario: User signup links guest donor

- **WHEN** a new user registers with phone `01712345678`
- **AND** a "Guest" donor record exists for `01712345678` tied to "Red Crescent"
- **THEN** the new user SHALL be automatically associated with the "Red Crescent" donor database.

### Requirement: Multi-Organization Donor Association

The system SHALL allow a single donor record to be associated with multiple organizations simultaneously.

#### Scenario: Donor across multiple networks

- **WHEN** "Org A" and "Org B" both import the same donor phone number
- **THEN** the donor's `organizations` list SHALL contain both "Org A" and "Org B".
