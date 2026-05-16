# GEMINI.md

READ AGENTS.md FIRST. This file contains Gemini-specific notes only.

## Guidance

- **Source of Truth**: All architectural and workflow decisions are defined in `AGENTS.md`.
- **Workflow**: You MUST use the Project Rokto OpenSpec workflow commands (`/opsx:*`) for all changes.
- **Verification**: Always run `just check` before concluding any implementation task.
- **Environment**: Use `uv` for dependency management and `just` for task orchestration.
