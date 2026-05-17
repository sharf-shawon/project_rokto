## Why

Several linting errors (Ruff) persist in the newly added test files. These errors prevent successful pre-commit checks and compromise the codebase's standard compliance. We need a targeted cleanup to resolve these final 9 issues.

## What Changes

- **Namespace Consistency**: Add missing `__init__.py` to test directories.
- **Magic Number Elimination**: Replace magic values with named constants or `HTTPStatus` codes.
- **Code Quality Refactor**:
  - Fix boolean positional values in function calls.
  - Move imports to the top level.
  - Remove unused local variables.
  - Fix import ordering.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `code-quality`: Strengthening the enforcement of zero linting errors.

## Impact

- **CI/CD**: `just check` and pre-commit hooks will pass.
- **Maintainability**: Improved test code readability.
