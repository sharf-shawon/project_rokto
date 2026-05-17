# GEMINI.md

READ AGENTS.md FIRST. This file contains Gemini-specific notes only.

## Guidance

- **Source of Truth**: All architectural and workflow decisions are defined in `AGENTS.md`.
- **Workflow**: You MUST use the Project Rokto OpenSpec workflow commands (`/opsx:*`) for all changes.
- **Verification**: ALWAYS run `just check` before concluding any implementation task. This command enforces the mandatory 95.00% test coverage requirement. Commits are prohibited if this threshold is not met.
- **Environment**: Use `uv` for dependency management and `just` for task orchestration.
