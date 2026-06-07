## Context

The Docker `entrypoint` script for the Django service constructs the `DATABASE_URL` at runtime. While this works for the main process (Gunicorn) and any command run via `docker compose run` (which uses the entrypoint), it fails for interactive commands like `docker exec -it <container> bash` because `docker exec` bypasses the entrypoint. Since `django-environ` is configured to expect `DATABASE_URL`, commands like `python manage.py` fail in these sessions.

## Goals / Non-Goals

**Goals:**

- Fix `ImproperlyConfigured` errors for `manage.py` commands in production shells.
- Automate `DATABASE_URL` construction in Django settings when missing.
- Maintain compatibility with existing environment variable management (Coolify/Docker).

**Non-Goals:**

- Modifying the Docker `entrypoint` (it is correct for its intended use).
- Hardcoding sensitive credentials.

## Decisions

### 1. Implement Fallback Logic in `config/settings/base.py`

- **Rationale**: By moving the construction logic (or a fallback version of it) into the Django settings, we ensure that the application is self-sufficient regardless of how the process was started.
- **Implementation**: Check for `DATABASE_URL` in the environment. If missing, attempt to build it using `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, and `POSTGRES_DB`.
- **Alternatives**: Forcing `exec` to use the entrypoint. _Rejected_ as it's complex and platform-dependent.

### 2. Match Entrypoint Logic Exactly

- **Rationale**: To prevent inconsistent database connections between Gunicorn and administrative tasks, the construction logic in `base.py` must match the `entrypoint` script exactly.

## Risks / Trade-offs

- **[Risk]** Redundant logic. → **Mitigation**: Small duplication is acceptable for operational reliability. The settings logic will only trigger if the entrypoint's export is missing.
- **[Risk]** Error masking. → **Mitigation**: If the component variables are also missing, `django-environ` will still throw an appropriate error, just deeper in the construction.
