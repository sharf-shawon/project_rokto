## ADDED Requirements

### Requirement: Per-Phone OTP Rate Limiting

The system SHALL limit the number of OTP SMS requests per phone number to prevent abuse and SMS spam. The limit SHALL be 5 OTP requests per phone number per rolling hour, enforced via Redis.

#### Scenario: Within limit

- **WHEN** a user requests an OTP for phone number `01712345678`
- **AND** the phone has made only 2 OTP requests in the last hour
- **THEN** the OTP SHALL be sent normally

#### Scenario: Rate limit exceeded

- **WHEN** a user requests an OTP for phone number `01712345678`
- **AND** the phone has made 5 OTP requests in the last hour
- **THEN** the OTP SHALL NOT be sent
- **AND** the user SHALL receive an error message indicating they should try again later
- **AND** the blocked attempt SHALL be logged to `SMSLog` with status=BLOCKED

### Requirement: Per-IP Rate Limiting on Auth Endpoints

The system SHALL limit the frequency of requests from a single IP address to OTP-generating endpoints (phone login, phone manage, phone verify) to prevent brute-force attacks. The limit SHALL be 1 request per 30 seconds per IP, enforced via Redis.

#### Scenario: Valid request timing

- **WHEN** a client IP makes an OTP request
- **AND** the last request from that IP was more than 30 seconds ago
- **THEN** the request SHALL be processed normally

#### Scenario: Too many requests

- **WHEN** a client IP makes an OTP request
- **AND** the last request from that IP was less than 30 seconds ago
- **THEN** the request SHALL be rejected with HTTP 429 Too Many Requests

### Requirement: Rate Limit Headers

The system SHALL include standard rate limit HTTP headers in responses from rate-limited endpoints.

#### Scenario: Rate limit headers present

- **WHEN** a response is returned from a rate-limited endpoint
- **THEN** the response SHALL include `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` headers

### Requirement: Redis-Based Rate Limit Storage

All rate limiting counters SHALL be stored in Redis with automatic TTL expiry aligned to their window duration.

#### Scenario: OTP rate limit key structure

- **WHEN** an OTP request is counted for phone number `01712345678`
- **THEN** the Redis key `otp_rate_limit:01712345678` SHALL be incremented
- **AND** the key SHALL have a TTL of 3600 seconds

#### Scenario: IP rate limit key structure

- **WHEN** a request is counted for IP `192.168.1.1`
- **THEN** the Redis key `ip_rate_limit:192.168.1.1` SHALL be set
- **AND** the key SHALL have a TTL of 30 seconds
