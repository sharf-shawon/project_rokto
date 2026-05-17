## MODIFIED Requirements

### Requirement: Mandatory Test Coverage

The system SHALL maintain a minimum of 95% total code coverage as measured by the `coverage` tool. This requirement SHALL be enforced by the local verification task runner and CI/CD pipelines.

#### Scenario: Coverage threshold enforcement

- **WHEN** developer runs `just check`
- **THEN** the system SHALL execute `just test-coverage`
- **AND** the command SHALL exit with a non-zero code if total coverage is below 95.00%.
