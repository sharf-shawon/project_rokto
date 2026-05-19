## ADDED Requirements

### Requirement: Self-Hosted URL Shortening

The system SHALL provide a self-hosted URL shortening service that converts long URLs into short, URL-safe codes suitable for SMS messages. The shortener SHALL use hashids to generate codes from integer IDs stored in the `ShortURL` model.

#### Scenario: Shortening a URL

- **WHEN** a system component requests a short URL for a long URL (e.g., an accept link for a blood request)
- **THEN** the URL shortener SHALL create or return an existing `ShortURL` record
- **AND** the short code SHALL be 6-8 characters long
- **AND** the short URL SHALL use the `SHORT_URL_DOMAIN` setting as its base

#### Scenario: Same URL returns same short code

- **WHEN** the same full URL is shortened twice
- **THEN** the same `ShortURL` record SHALL be returned (deduplication)
- **AND** no duplicate database entry SHALL be created

### Requirement: Short URL Resolution

The system SHALL resolve short codes to their original URLs via a Django view, performing a 302 redirect.

#### Scenario: Resolving a short code

- **WHEN** a user agent requests `https://SHORT_URL_DOMAIN/<code>`
- **THEN** the system SHALL look up the `ShortURL` by code
- **AND** issue a 302 redirect to the original URL

#### Scenario: Invalid short code

- **WHEN** a user agent requests an unknown or expired short code
- **THEN** the system SHALL return HTTP 404

### Requirement: Short URL Expiry

Short URLs SHALL have configurable expiry times to prevent stale links from being used indefinitely.

#### Scenario: Default expiry

- **WHEN** a `ShortURL` is created without explicit expiry
- **THEN** it SHALL default to 30 days for OTP-related URLs
- **AND** 7 days for donation/notification-related URLs

#### Scenario: Expired URL

- **WHEN** a user agent requests an expired short code
- **THEN** the system SHALL return HTTP 404
