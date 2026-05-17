## Context

Current test coverage is 89.98%. The primary gaps are in `organizations` (API, Admin, Tasks) and `blood_requests` (Views). While `pyproject.toml` is configured to fail under 95%, the standard `just check` command bypasses this check by running only standard `pytest`.

## Goals / Non-Goals

**Goals:**

- Upgrade `just check` to enforce the 95% coverage requirement locally.
- Reach 95.00% total coverage by adding missing test cases.
- Formalize coverage enforcement in project documentation.

**Non-Goals:**

- Aiming for 100% coverage (95% is the mandated threshold).
- Refactoring production code (except where necessary to make it testable).

## Decisions

### 1. Unified Verification Command

- **Decision**: Update `justfile`'s `check` command to execute `just test-coverage`.
- **Rationale**: Ensures that developers cannot consider a task "finished" without verifying that coverage hasn't regressed.

### 2. Targeted Coverage Injection

- **Decision**: Focus on the following specific files for new tests:
  - `project_rokto/organizations/api/views.py` (Currently 55%)
  - `project_rokto/organizations/admin.py` (Currently 58%)
  - `project_rokto/organizations/tasks.py` (Currently 75%)
  - `project_rokto/blood_requests/views.py` (Currently 83%)
- **Approach**: Identify uncovered lines using `coverage html` and write unit/integration tests to exercise those paths (e.g., error handling, permission checks, edge cases).

## Risks / Trade-offs

- **[Risk] Slower feedback loop** → `test-coverage` is slightly slower than `test`.
  - **Mitigation**: `test-coverage` still only takes seconds in this environment; the trade-off for reliability is worth the minor latency.
- **[Risk] Brittle tests** → Writing tests just for "lines" can lead to brittle suites.
  - **Mitigation**: Focus on functional requirements (e.g., "Non-admin cannot upload CSV") rather than just line coverage.
