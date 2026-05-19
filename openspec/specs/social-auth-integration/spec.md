## ADDED Requirements

### Requirement: Social Auth Provider Support

The system SHALL support Google and Facebook as social authentication providers.

#### Scenario: Social login button visibility

- **WHEN** a user visits any login or signup page
- **THEN** they SHALL see buttons to "Login with Google" and "Login with Facebook"

### Requirement: Automatic Email Account Linking

The system SHALL automatically link a social account to an existing user account if the social account's email matches the existing user's email.

#### Scenario: Linking social account to phone-signup user

- **WHEN** a user who previously signed up via phone (and added an email) logs in via Google with the same email
- **THEN** the system SHALL authenticate them into their existing account

### Requirement: Phone Verification Enforcement for Social Users

The system SHALL require users who sign up via social accounts to verify a phone number before they can access core protected features, maintaining the trust model of the platform.

#### Scenario: Social signup redirection to phone verification

- **WHEN** a new user signs up via Google
- **THEN** they SHALL be redirected to the phone verification flow by the `VerificationMiddleware` before accessing the dashboard
