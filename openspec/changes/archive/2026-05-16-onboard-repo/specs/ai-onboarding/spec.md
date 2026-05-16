## ADDED Requirements

### Requirement: Single Source of Truth for AI Agents

AI agents SHALL prioritize `AGENTS.md` as the primary source of truth for repository-wide coding standards, architectural decisions, and development workflows.

#### Scenario: Agent researches project conventions

- **WHEN** an AI agent enters the repository
- **THEN** it reads `AGENTS.md` first and follows the "Development Lifecycle" and "Quality Expectations" defined therein.

### Requirement: OpenSpec Workflow Compliance

All AI-driven changes SHALL follow the OpenSpec `/opsx:*` workflow commands (explore, propose, apply, archive) to manage the change lifecycle.

#### Scenario: Agent starts a new feature

- **WHEN** an agent is asked to implement a feature
- **THEN** it uses `/opsx:propose` to create artifacts before writing application code.

### Requirement: Justfile and UV Usage

AI agents SHALL use `just` for task execution (up, migrate, test, check) and `uv` for dependency management as specified in the project configuration.

#### Scenario: Agent running quality checks

- **WHEN** an agent completes a code change
- **THEN** it executes `just check` to verify linting, typing, and tests.
