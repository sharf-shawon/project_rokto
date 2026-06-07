# build-infrastructure Specification

## Purpose

TBD - created by archiving change fix-production-build-missing-git. Update Purpose after archive.

## Requirements

### Requirement: Production Build Git Support

The production build system SHALL support fetching dependencies from Git repositories.

#### Scenario: Successful dependency resolution with Git source

- **WHEN** the Docker build process runs `uv sync`
- **THEN** the system MUST be able to execute `git` to fetch remote repositories

### Requirement: Production Runtime Security

The production environment SHALL include standard CA certificates to support secure outbound communication.

#### Scenario: Successful HTTPS API call

- **WHEN** the Django application makes an outbound HTTPS request to a service like MimSMS
- **THEN** the request MUST succeed without SSL certificate verification errors

### Requirement: Platform-Managed Reverse Proxy Compatibility

The production infrastructure SHALL support deployments where the reverse proxy is managed by the host platform (e.g., Coolify).

#### Scenario: Stack starts without port conflicts

- **WHEN** the Docker Compose stack is started on a host where ports 80 and 443 are already allocated
- **THEN** the project's internal services MUST NOT attempt to bind to those host ports

### Requirement: Resilient S3 Compatibility

The production infrastructure SHALL support robust interaction with S3-compatible object storage providers (e.g., Cloudflare R2, MinIO, AWS).

#### Scenario: Successful static file collection

- **WHEN** the `collectstatic` command is executed with `collectfasta` enabled
- **THEN** the storage backend MUST successfully list and upload objects using path-style addressing and explicit endpoint resolution without `NoSuchKey` errors

### Requirement: Consistent Environment Variable Resilience

The system SHALL support execution even when core environment variables like `DATABASE_URL` are not explicitly exported by the host environment or entrypoint, as long as their component parts (e.g., `POSTGRES_USER`, `POSTGRES_PASSWORD`, etc.) are available.

#### Scenario: Administrative command in interactive shell

- **WHEN** a `manage.py` command is run in a shell session where `DATABASE_URL` is missing
- **THEN** the application MUST automatically construct the database configuration from individual `POSTGRES_*` variables and proceed successfully
