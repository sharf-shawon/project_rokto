## 1. Migration File Cleanup

- [x] 1.1 Remove all migration files in `project_rokto/donors/migrations/` except `__init__.py`.
- [x] 1.2 Remove all migration files in `project_rokto/users/migrations/` except `__init__.py`.
- [x] 1.3 Remove all migration files in `project_rokto/blood_requests/migrations/` except `__init__.py`.
- [x] 1.4 Remove all migration files in `project_rokto/locations/migrations/` except `__init__.py`.
- [x] 1.5 Remove all migration files in `project_rokto/organizations/migrations/` except `__init__.py`.

## 2. Database Purge

- [x] 2.1 Drop the existing local PostgreSQL database or run `just manage flush --no-input`.
- [x] 2.2 Re-verify that the `django_migrations` table is empty or the database is fresh.

## 3. Fresh Initialization

- [x] 3.1 Run `just manage makemigrations` to generate fresh `0001_initial.py` files for all apps.
- [x] 3.2 Run `just manage migrate` to apply the fresh migrations and build the schema.

## 4. Verification

- [x] 4.1 Run `just check` to ensure all tests pass with the new schema.
- [x] 4.2 Verify that the `phone_number` column exists in the `donors_donor` table via `inspectdb` or ORM check.
