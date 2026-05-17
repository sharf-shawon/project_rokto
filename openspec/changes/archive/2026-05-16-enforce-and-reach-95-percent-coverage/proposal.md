## Why

The project has a strict mandate for 95% total code coverage to ensure reliability and prevent regressions in the life-saving infrastructure of Project Rokto. Currently, the coverage stands at approximately 90%, and the task runner (`just check`) only runs basic tests without enforcement. We need to close this 5% "coverage debt" and upgrade our verification tools to prevent future commits from falling below this threshold.

## What Changes

- **Coverage Enforcement**: Update `just check` to run `test-coverage` instead of standard `test`, making the 95% threshold a hard gate for local verification.
- **Instruction Update**: Explicitly document the coverage requirement in `AGENTS.md` and `GEMINI.md` as a foundational engineering standard.
- **Debt Reduction**: Add targeted unit and integration tests for low-coverage modules, specifically focusing on `organizations` and `blood_requests`.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `code-quality`: Update requirements to include mandatory 95% coverage enforcement.

## Impact

- **CI/CD & Local Dev**: `just check` will now fail if coverage is below 95%.
- **Testing Suite**: New test files and cases will be added to the codebase.
- **Project Governance**: Coverage becomes a non-negotiable standard for all contributors.
