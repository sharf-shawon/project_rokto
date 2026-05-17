## Context

9 persistence linting errors remain in the test suite across `donors`, `organizations`, and `users` apps.

## Goals / Non-Goals

**Goals:**

- Fix all 9 linting errors precisely.
- Ensure all tests continue to pass.
- Satisfy the 95% coverage requirement.

## Decisions

### 1. Specific Fixes

- `project_rokto/donors/tests/test_admin.py`: Add `__init__.py`, replace magic number `2` with `EXPECTED_MIN_DONORS`, and pass `change=False` as keyword.
- `project_rokto/organizations/tests/test_admin.py`: Replace magic number `2` with `EXPECTED_ORG_COUNT`.
- `project_rokto/organizations/tests/test_api.py`: Move `DonorImportService` import to top.
- `project_rokto/organizations/tests/test_middleware.py`: Replace `302` with `HTTPStatus.FOUND`.
- `project_rokto/organizations/tests/test_tasks.py`: Move `patch` import to top.
- `project_rokto/users/tests/test_forms_coverage.py`: Remove unused `saved_user` assignment.

## Risks / Trade-offs

- **[Risk]** Accidental test breaking during refactor.
  - **Mitigation**: Run tests immediately after fixing each file.
