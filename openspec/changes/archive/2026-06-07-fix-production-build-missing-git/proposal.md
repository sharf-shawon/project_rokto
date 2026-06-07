## Why

The production Docker build is currently failing because the `uv sync` command requires `git` to fetch the `django-mimsms` dependency from a Git source. The current production base image is a slim version that lacks both `git` and `ca-certificates`, causing the build to error out during dependency resolution.

## What Changes

- **Modify Dockerfile (Production)**: Update the `python-build-stage` to install `git` and `ca-certificates`.
- **Modify Dockerfile (Production)**: Update the `python-run-stage` to install `ca-certificates` to support secure outbound API calls (MimSMS).
- **Optimize Image Layers**: Combine `apt-get install` and `rm -rf /var/lib/apt/lists/*` to maintain image efficiency.

## Capabilities

### New Capabilities

- `build-infrastructure`: Production build environment and runtime security configuration.

### Modified Capabilities

- None

## Impact

- **Build Infrastructure**: Fixes the broken CI/CD pipeline for production deployments.
- **Production Environment**: Enhances security and reliability of outbound API requests by providing standard root certificates.
- **Files**: `compose/production/django/Dockerfile`
