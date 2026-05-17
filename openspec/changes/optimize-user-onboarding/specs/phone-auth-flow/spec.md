## ADDED Requirements

### Requirement: Phone-based authentication

Users SHALL be able to sign in or sign up using only their phone number via OTP. The phone login/signup flow SHALL be a single unified path where entering a phone number and verifying via OTP either logs in an existing user or creates a new account.

#### Scenario: Existing user logs in via phone

- **WHEN** an existing user enters their phone number and verifies with a valid OTP
- **THEN** they are logged in and redirected to their profile page

#### Scenario: New user signs up via phone

- **WHEN** a new user enters their phone number and verifies with a valid OTP
- **THEN** they are prompted to provide their name (email optional), and after submission, their account is created and they are logged in

#### Scenario: New user has phone verified on creation

- **WHEN** a new user completes phone signup (enters name)
- **THEN** their `is_phone_verified` field SHALL be set to `True` at account creation
- **THEN** the VerificationMiddleware SHALL NOT redirect them to phone verification again

#### Scenario: Phone login page shows all auth options

- **WHEN** a user visits the phone login page
- **THEN** they SHALL see links to email-based login and email-based signup as alternatives

#### Scenario: Invalid OTP cannot authenticate

- **WHEN** a user submits an invalid or expired OTP
- **THEN** an error message SHALL be displayed
- **THEN** the user SHALL NOT be logged in or redirected to signup

### Requirement: Phone auth UI communicates dual purpose

The phone login page heading and description SHALL clearly communicate that it handles both sign in AND sign up.

#### Scenario: Phone page heading clarifies dual purpose

- **WHEN** a user navigates to the phone auth page
- **THEN** the heading SHALL indicate it is for both signing in and signing up (e.g., "Sign In / Sign Up with Phone")
- **THEN** the description SHALL explain the flow (e.g., "Enter your phone number to sign in or create a new account.")

### Requirement: Cross-reference between auth paths

All auth pages (phone login, email login, email signup) SHALL contain links to the other available auth methods.

#### Scenario: All auth pages reference each other

- **WHEN** a user visits any auth page
- **THEN** they SHALL see links to the other authentication methods (phone, email login, email signup)

#### Scenario: Navbar shows phone auth option

- **WHEN** a user is not authenticated
- **THEN** the navigation bar SHALL display a "Phone Sign In / Up" link alongside the email-based "Sign Up" and "Sign In" links
