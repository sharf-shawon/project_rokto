## Context

The project is being deployed to Coolify, which manages its own reverse proxy (Traefik). The default `docker-compose.production.yml` from `cookiecutter-django` includes a `traefik` service that maps to host ports 80 and 443. This causes a `Bind for 0.0.0.0:80 failed` error when Coolify attempts to start the stack.

## Goals / Non-Goals

**Goals:**

- Eliminate port conflicts with the host platform (Coolify).
- Follow Coolify best practices for Docker Compose deployments by using the platform's ingress.
- Ensure the `django` service is correctly configured to be reached on port 5000.

**Non-Goals:**

- Removing the Traefik Dockerfile or configuration files from the repository (they may be needed for other deployment targets).
- Changing the local development proxy setup.

## Decisions

### 1. Comment out `traefik` service in `docker-compose.production.yml`

- **Rationale**: Since Coolify provides a superior, centrally managed Traefik instance, running a second Traefik inside the stack is redundant and causes port conflicts.
- **Alternatives**: Changing host ports to 8080/8443. _Rejected_ as it adds unnecessary complexity and requires double-proxying.

### 2. Remove `production_traefik` volume from `docker-compose.production.yml`

- **Rationale**: This volume is only used for ACME certificates by the stack-internal Traefik. Coolify manages its own certificates.

## Risks / Trade-offs

- **[Risk]** Loss of custom Traefik middleware. → **Mitigation**: Any required middleware should be configured via Coolify's UI/Labels.
- **[Risk]** Static file serving issues. → **Mitigation**: Static files are already offloaded to S3 in the production settings, so Traefik was not serving them anyway.
