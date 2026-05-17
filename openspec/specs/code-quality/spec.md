# code-quality Specification

## ADDED Requirements

### Requirement: Lint Compliance

The system SHALL adhere to all linting and code quality rules defined in the project's Ruff configuration.

#### Scenario: Code verification passes

- **WHEN** developer runs `just check`
- **THEN** all linting, formatting, and type-checking tasks MUST pass without errors.

### Requirement: Mandatory Test Coverage

The system SHALL maintain a minimum of 95% total code coverage as measured by the `coverage` tool. This requirement SHALL be enforced by the local verification task runner and CI/CD pipelines.

#### Scenario: Coverage threshold enforcement

- **WHEN** developer runs `just check`
- **THEN** the system SHALL execute `just test-coverage`
- **AND** the command SHALL exit with a non-zero code if total coverage is below 95.00%.
