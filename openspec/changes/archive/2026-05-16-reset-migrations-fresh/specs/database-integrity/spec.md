## ADDED Requirements

### Requirement: Database Schema Consistency

The system SHALL ensure that the database schema is always in sync with the migration files.

#### Scenario: Fresh database initialization

- **WHEN** all migration files are reset and the database is purged
- **THEN** running `makemigrations` and `migrate` SHALL result in a functional database schema that matches the models.
