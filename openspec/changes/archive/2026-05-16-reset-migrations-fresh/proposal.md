## Why

The database schema has become inconsistent with the existing migration files, particularly in the `donors` app where a critical column (`phone_number`) is missing from the database but expected by the codebase. To resolve these discrepancies and ensure a clean, reliable state for development, a project-wide reset of all migrations is necessary.

## What Changes

- **Migration Cleanup**: Removal of all existing migration files across all Django apps in the project (excluding `__init__.py`).
- **Database Reset**: Complete purge of the local database to eliminate schema inconsistencies and the outdated `django_migrations` history.
- **Fresh Initialization**: Generation of new `0001_initial` migrations for all apps based on the current state of the models.
- **Data Wipe**: **BREAKING** This change will result in the loss of all local development data.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- None (This is an infrastructure/maintenance change).

## Impact

- **Database**: All tables will be dropped and recreated.
- **Migrations**: Every app's `migrations/` directory will be updated with a fresh initial state.
- **Development Workflow**: All team members will need to reset their local databases after this change is merged.
