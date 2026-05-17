## Why

The `celerybeat` service is currently failing with a `django.db.utils.ProgrammingError` because it cannot find the required database tables for `django_celery_beat`. This indicates that although the multi-channel notification system was recently implemented, the database schema for the scheduler is not correctly initialized or the service is attempting to start before migrations are complete.

## What Changes

- **Migration Verification**: Re-run and verify all migrations, specifically focusing on `django_celery_beat`.
- **Startup Sequence**: Ensure that the `celerybeat` service in `docker-compose.local.yml` waits for migrations to be successfully applied before attempting to start the scheduler.
- **Environment Consistency**: Verify that all Celery-related services are using the correct database configuration and volume persistence.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `notification-dispatcher`: Ensuring the scheduler component of the dispatcher is reliably initialized.

## Impact

- **Infrastructure**: Updates to `docker-compose.local.yml` and potentially the `start-celerybeat` script.
- **Stability**: Resolves the crash loop in the `celerybeat` container.
- **Reliability**: Ensures that scheduled tasks (like quota resets) are executed correctly.
