## ADDED Requirements

### Requirement: Optional Email Authentication

The system SHALL allow users to sign up and log in via email and password without requiring email verification to access core functionality.

#### Scenario: Signup with optional email verification

- **WHEN** a user signs up with an email and password
- **THEN** they SHALL be allowed to log in and access protected pages immediately, even if their email is not yet verified

### Requirement: Optional Email in User Profiles

The system SHALL allow users to create and update their profiles without providing an email address.

#### Scenario: Phone-based signup without email

- **WHEN** a user completes phone OTP verification and reaches the signup info form
- **THEN** they SHALL be able to submit the form and create an account by providing only their name, leaving the email field blank

### Requirement: Phone Signup Auto-Verification

The system SHALL mark users who sign up via the Phone OTP flow as phone-verified immediately upon account creation.

#### Scenario: New user signs up via phone

- **WHEN** a new user successfully verifies their phone via OTP and provides their name
- **THEN** their account SHALL be created with `is_phone_verified=True`

### Requirement: Verification Middleware Exemptions

The system SHALL allow authenticated users to access their own profile detail page and allow superusers to bypass all verification checks (NID and Phone).

#### Scenario: Superuser bypass

- **WHEN** a superuser is logged in and accesses any protected page
- **THEN** the system SHALL NOT redirect them to NID or Phone verification pages

#### Scenario: Unverified user profile access

- **WHEN** an authenticated but unverified user accesses their own profile page (`/users/<username>/`)
- **THEN** the system SHALL allow access without redirecting to verification pages

### Requirement: Account Recovery Nudge

The system SHALL display a warning or "nudge" to users who have a verified phone but have not set an email or password, advising them to add recovery options.

#### Scenario: Nudge visibility for phone-only users

- **WHEN** a user with a verified phone but no email and no usable password views their own profile page
- **THEN** the system SHALL display a notification or card suggesting they add an email and set a password
