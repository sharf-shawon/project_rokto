## 1. Production Dockerfile Updates

- [x] 1.1 Add `git` and `ca-certificates` to `python-build-stage` in `compose/production/django/Dockerfile`
- [x] 1.2 Add `ca-certificates` to `python-run-stage` in `compose/production/django/Dockerfile`
- [x] 1.3 Ensure `apt-get` cache cleanup is properly handled in both stages to minimize image size

## 2. Verification

- [x] 2.1 Verify that `git` is successfully found by `uv` during build
- [x] 2.2 Verify that `ca-certificates` are installed in the final production image
- [x] 2.3 Run `just check` to verify workspace integrity
