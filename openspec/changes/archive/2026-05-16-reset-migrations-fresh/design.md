## Context

The project has multiple Django apps (`donors`, `users`, `blood_requests`, `locations`, `organizations`) with independent migration histories. A recent set of manual or corrupted migrations has left the database schema out of sync with the migration files. Standard recovery attempts (like `makemigrations`) are ineffective because the files incorrectly state that the schema is up to date.

## Goals / Non-Goals

**Goals:**

- Completely remove all existing migration files.
- Purge all database tables and migration history.
- Re-initialize all apps with clean `0001_initial.py` files.
- Ensure all automated tests pass with the fresh schema.

**Non-Goals:**

- Preserving any existing development data.
- Refactoring models or business logic during this reset.

## Decisions

### 1. Hard Reset of Migration Files

- **Decision**: Physically delete all files matching `project_rokto/*/migrations/*.py` except for `__init__.py`.
- **Rationale**: This is the only way to ensure that Django "forgets" the previous corrupted state and starts a fresh dependency graph.

### 2. Database Recreation via `sqlflush` or `dropdb`

- **Decision**: Use `docker compose run --rm django python manage.py flush` or a full container recreate to clear the database.
- **Rationale**: Given the schema is inconsistent, a simple `flush` might fail if table definitions are broken. A full drop and recreate is more reliable.

### 3. Unified Fresh Initialization

- **Decision**: Run a single `makemigrations` command for all apps simultaneously.
- **Rationale**: Ensures that cross-app foreign key dependencies are correctly mapped in the new `0001` files.

## Risks / Trade-offs

- **[Risk] Broken Dependencies** → Cross-app foreign keys might cause `makemigrations` to fail if app ordering is incorrect.
  - **Mitigation**: Run `makemigrations` globally so Django can resolve the graph automatically.
- **[Risk] Lost Business Logic in Migrations** → If any custom `RunPython` logic existed in previous migrations, it will be lost.
  - **Mitigation**: Review existing migrations for custom logic before deletion. (Initial research suggests standard schema-only migrations).
