## 1. Tooling & Documentation

- [x] 1.1 Update `justfile`'s `check` command to run `just test-coverage`.
- [x] 1.2 Update `AGENTS.md` to emphasize coverage threshold in the Verification section.
- [x] 1.3 Update `GEMINI.md` to reinforce `just check` as the mandatory pre-commit gate.

## 2. Coverage Debt Reduction (Organizations)

- [x] 2.1 Add unit tests for `project_rokto/organizations/api/views.py` (permission edge cases, field validation).
- [x] 2.2 Add unit tests for `project_rokto/organizations/admin.py` (custom actions, queryset filtering).
- [x] 2.3 Add unit tests for `project_rokto/organizations/tasks.py` (failure modes, quota logging).

## 3. Coverage Debt Reduction (Blood Requests)

- [x] 3.1 Add integration tests for `project_rokto/blood_requests/views.py` covering all redirection and error paths.
- [x] 3.2 Verify total coverage reaches 95.00% using `just test-coverage`.

## 4. Final Validation

- [x] 4.1 Run `just check` to ensure all quality gates (lint, type, coverage) pass.
