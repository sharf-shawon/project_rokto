## Context

The previous implementation of PII consolidation and notifications introduced several non-compliant code patterns according to the project's Ruff configuration.

## Goals / Non-Goals

**Goals:**

- Fix all 10 reported linting errors.
- Ensure `just check` passes without errors.
- Maintain existing functionality while improving code quality.

## Decisions

### 1. Specific Exception Handling

- **Decision**: Replace `except Exception as e` with more specific exceptions where possible, or use `logging.exception()` to capture context if broad catching is unavoidable for robustness.
- **Rationale**: Blindly catching `Exception` hides bugs and makes debugging harder.

### 2. Standardized Status Codes

- **Decision**: Use `http.HTTPStatus` constants instead of magic numbers like `302`.
- **Rationale**: Improves code readability and self-documentation.

### 3. Namespace Integrity

- **Decision**: Add `__init__.py` to `project_rokto/organizations/tests/`.
- **Rationale**: Avoids implicit namespace packages which can lead to import issues in some environments.

## Risks / Trade-offs

- **[Risk]** Breaking functionality during refactor of `try/except` blocks.
  - **Mitigation**: Run existing tests after every small change to ensure no regression.
