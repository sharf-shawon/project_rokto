## Context

The `celerybeat` service uses `django_celery_beat.schedulers:DatabaseScheduler`, which stores the schedule in the database. When the container starts, it attempts to query `django_celery_beat_crontabschedule`. If the migrations haven't run or the database is being initialized, it throws a `ProgrammingError`.

## Goals / Non-Goals

**Goals:**

- Resolve the `ProgrammingError` in the `celerybeat` container.
- Ensure `celerybeat` only starts after the database is ready and migrations are applied.
- Maintain a clean and automated local development setup.

**Non-Goals:**

- Changing the scheduler type (DatabaseScheduler is desired for flexibility).
- Refactoring the `django-mimsms` or notification dispatcher logic.

## Decisions

### 1. Unified Startup Script for Celery Beat

- **Decision**: Update `/start-celerybeat` to include a `python manage.py migrate` check or a wait-for-migrations logic.
- **Rationale**: Since `celerybeat` is part of the same application as `django`, it's safe and robust to ensure its own dependencies are met before it starts.

### 2. Dependency Ordering in Docker Compose

- **Decision**: Add a healthcheck to the `django` service or use an explicit wait-for in the `celerybeat` service command.
- **Rationale**: Currently `celerybeat` only `depends_on: postgres`, but it actually depends on the schema being initialized by the `django` service's startup process (which usually runs migrations).

### 3. Explicit Migration Command

- **Decision**: Trigger a manual `migrate django_celery_beat` if the automatic migrations were skipped.
- **Rationale**: Double-checking the application of third-party migrations is a low-cost, high-reward stability measure.

## Risks / Trade-offs

- **[Risk] Race Condition** → Both `django` and `celerybeat` might try to run migrations simultaneously.
  - **Mitigation**: Use `wait-for-it` on the `django` service port or implement a lock-aware migration check.
