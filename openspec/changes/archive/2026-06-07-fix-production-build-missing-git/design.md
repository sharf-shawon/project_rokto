## Context

The project uses `uv` for Python package management. For production, the Django image is built using a multi-stage Dockerfile. The build stage currently lacks `git`, which is required by `uv` to resolve and fetch dependencies specified as Git sources (specifically `django-mimsms`). Additionally, the production environment requires `ca-certificates` to securely interact with the MimSMS API and other external services.

## Goals / Non-Goals

**Goals:**

- Fix the broken production build by providing the necessary tools (`git`) to `uv` during the dependency synchronization phase.
- Ensure the production runtime environment can verify SSL/TLS certificates for outbound API requests.
- Maintain minimal production image size by using multi-stage builds effectively.

**Non-Goals:**

- Refactoring the entire Dockerfile or changing base image distributions.
- Moving the Git dependency to a private PyPI mirror at this time.

## Decisions

### 1. Install `git` and `ca-certificates` in `python-build-stage`

- **Rationale**: `uv` delegates Git operations to the system's `git` executable. `ca-certificates` is required for `git` to verify the identity of GitHub/GitLab servers over HTTPS.
- **Alternatives**: Using a full (non-slim) image. _Rejected_ because it adds significant unnecessary bloat (~200MB+).

### 2. Install `ca-certificates` in `python-run-stage`

- **Rationale**: The `django-mimsms` library (and potentially others) makes outbound HTTPS requests. Without root certificates, these requests will fail with "certificate verify failed" errors.
- **Alternatives**: Disabling SSL verification in the application. _Rejected_ as it is a severe security risk.

### 3. Layer Optimization via Combined `apt` Commands

- **Rationale**: Combining `apt-get update`, `install`, and `rm -rf /var/lib/apt/lists/*` in a single `RUN` command ensures that the metadata for `apt` packages is not persisted in the image layer, keeping the build lean.

## Risks / Trade-offs

- **[Risk]** Image size increase. → **Mitigation**: `git` is only installed in the build stage; only `ca-certificates` (~1MB) is added to the final production image.
- **[Risk]** Slower build times. → **Mitigation**: Using Docker BuildKit cache mounts (`--mount=type=cache,target=/var/lib/apt/lists/`) where possible to speed up package installation.
