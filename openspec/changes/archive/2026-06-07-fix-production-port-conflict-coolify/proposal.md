## Why

The production deployment is failing because the project's `traefik` service is attempting to bind to ports 80 and 443, which are already allocated by Coolify's built-in reverse proxy. This creates a port conflict that prevents the application stack from starting.

## What Changes

- **Modify `docker-compose.production.yml`**: Comment out or remove the `traefik` service and its associated volume/network configurations.
- **Adjust Django Service**: Ensure the `django` service is prepared to be reached directly by the external proxy (Coolify) on its internal port (5000).

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `build-infrastructure`: Update production infrastructure requirements to support platform-managed reverse proxies.

## Impact

- **Production Deployment**: Resolves the port conflict, allowing the stack to start successfully on Coolify.
- **Network Architecture**: Shifts reverse proxy responsibility from the application stack to the host platform.
- **Files**: `docker-compose.production.yml`, `openspec/specs/build-infrastructure/spec.md`
