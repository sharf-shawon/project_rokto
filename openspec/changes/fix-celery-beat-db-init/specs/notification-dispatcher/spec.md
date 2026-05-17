## ADDED Requirements

### Requirement: Reliable Scheduler Initialization

The system SHALL ensure that the Celery Beat scheduler service only starts after all database migrations, specifically those for `django_celery_beat`, have been successfully applied.

#### Scenario: Startup with pending migrations

- **WHEN** the docker-compose environment is starting
- **AND** the `django_celery_beat` tables are not yet present in the database
- **THEN** the `celerybeat` service SHALL wait for the migration process to complete before attempting to initialize the scheduler.
