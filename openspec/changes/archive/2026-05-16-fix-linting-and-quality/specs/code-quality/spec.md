## ADDED Requirements

### Requirement: Lint Compliance

The system SHALL adhere to all linting and code quality rules defined in the project's Ruff configuration.

#### Scenario: Code verification passes

- **WHEN** developer runs `just check`
- **THEN** all linting, formatting, and type-checking tasks MUST pass without errors.
