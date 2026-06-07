## ADDED Requirements

### Requirement: Consistent Environment Variable Resilience

The system SHALL support execution even when core environment variables like `DATABASE_URL` are not explicitly exported by the host environment or entrypoint, as long as their component parts (e.g., `POSTGRES_USER`, `POSTGRES_PASSWORD`, etc.) are available.

#### Scenario: Administrative command in interactive shell

- **WHEN** a `manage.py` command is run in a shell session where `DATABASE_URL` is missing
- **THEN** the application MUST automatically construct the database configuration from individual `POSTGRES_*` variables and proceed successfully
