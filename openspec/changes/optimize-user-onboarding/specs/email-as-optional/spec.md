## ADDED Requirements

### Requirement: Email is optional during signup

Users SHALL NOT be required to provide an email address when signing up. The signup form SHALL accept email as an optional field in both the allauth email/password signup and the phone OTP signup flow.

#### Scenario: Allauth signup allows skipping email

- **WHEN** a user signs up via allauth email/password form
- **THEN** the email field SHALL NOT be marked as required
- **THEN** the user SHALL be able to complete signup without entering an email

#### Scenario: Phone signup allows skipping email

- **WHEN** a new user completes phone signup via the info form
- **THEN** the email field SHALL be optional
- **THEN** the user SHALL be able to complete signup with only a name

### Requirement: Email verification is not blocking

Email verification SHALL NOT be mandatory. Users with an email address MAY optionally verify it, but unverified email SHALL NOT prevent access to the site.

#### Scenario: User can access site without email verification

- **WHEN** a user signs up without providing an email or with an unverified email
- **THEN** they SHALL be able to log in and access all authenticated pages (subject to other verifications like NID and phone)

### Requirement: Email remains available as optional channel

Users MAY add or verify their email at any time after signup. The email management interface SHALL remain accessible from the profile page.

#### Scenario: User can add email later

- **WHEN** a user navigates to their profile
- **THEN** they SHALL see an option to add or manage their email
- **THEN** there SHALL be no forced email verification requirement
