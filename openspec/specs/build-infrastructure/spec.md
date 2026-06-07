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
