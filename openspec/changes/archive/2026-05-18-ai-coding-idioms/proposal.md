## Why

The project utilizes a highly strict Ruff configuration with opinionated rules (e.g., FBT, TRY, EM, SIM, PL, BLE, SLF) to ensure maximum code quality and security. By default, AI agents write generic "idiomatic Python," which frequently violates these strict project-specific rules. This leads to extensive rework loops and failed local CI checks. We need to codify these rules explicitly in plain English within the project specifications so AI agents write compliant code on their first attempt.

## What Changes

- Add a new "AI-Aware Coding Idioms" section to the existing `code-quality` specification.
- Explicitly define rules for Exception Handling (no string literals in exceptions, use `logger.exception`, suppress instead of `pass`).
- Explicitly define rules for Control Flow (no boolean positional arguments, prioritize ternary operators).
- Explicitly define rules for Variables and Clean Code (no magic numbers, top-level imports only, unused variable prefixing, no private member access).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `code-quality`: Adding explicit AI-aware coding idioms derived from the project's strict Ruff configuration (FBT, TRY, EM, SIM, PL).

## Impact

- **AI Agents**: Agents will parse the updated specification before writing code, resulting in higher first-pass success rates.
- **Development Workflow**: Reduces the time spent fixing lint errors across implementation tasks.
- **Codebase**: No direct changes to existing application code, only specification updates to guide future development.
