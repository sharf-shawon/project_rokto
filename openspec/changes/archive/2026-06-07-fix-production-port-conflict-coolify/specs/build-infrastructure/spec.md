## ADDED Requirements

### Requirement: Platform-Managed Reverse Proxy Compatibility

The production infrastructure SHALL support deployments where the reverse proxy is managed by the host platform (e.g., Coolify).

#### Scenario: Stack starts without port conflicts

- **WHEN** the Docker Compose stack is started on a host where ports 80 and 443 are already allocated
- **THEN** the project's internal services MUST NOT attempt to bind to those host ports
