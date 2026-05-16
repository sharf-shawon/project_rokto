## Context

The repository has accumulated multiple AI instruction files from different contributors and experiments (Gemini, Claude, Copilot, Codex). This "instruction bloat" leads to conflicting guidance and increased context token usage. The project also lacks formal requirement specifications in a machine-readable or standardized format (OpenSpec).

## Goals / Non-Goals

**Goals:**

- Eliminate redundant AI instruction files.
- Establish `AGENTS.md` as the single source of truth for repository context and coding standards.
- Bootstrap OpenSpec `specs/` for core domain logic.
- Align AI workflows with the Project Rokto development lifecycle.

**Non-Goals:**

- Modifying application code or business logic.
- Replacing project documentation for human users (`README.md`).
- Designing new features (this is purely an administrative/infrastructure change).

## Decisions

- **Decision: `AGENTS.md` as SSoT**
  - **Rationale**: It is the most comprehensive and well-structured file currently in the repo. It already follows a professional lifecycle (TRIAGE, CLARIFY, PLAN, etc.).
  - **Alternatives**: Using `GEMINI.md` or `CODEX.md`. Rejected because `AGENTS.md` is provider-agnostic and more detailed.

- **Decision: Thin out `GEMINI.md` and `CLAUDE.md`**
  - **Rationale**: Instead of deleting them immediately (which might break some IDE integrations), they will be reduced to minimal "loaders" that point to `AGENTS.md` and specify only provider-specific tool settings.
  - **Alternatives**: Complete deletion. Rejected to maintain compatibility with existing tool configurations that might look for these specific filenames.

- **Decision: Immediate Deletion of `.github/COOKIE-CUTTER-AGENT.md`**
  - **Rationale**: This file is actively harmful as it describes a different project (the generator) than what is actually in this repo (the generated app).

- **Decision: Extract Specs from Existing Code**
  - **Rationale**: To provide a baseline for future work, we will reverse-engineer specs for the `blood-request-lifecycle` and `donor-privacy-security` from the current Django models and views. This ensures future AI agents don't accidentally regress core security or functional logic.

## Risks / Trade-offs

- **[Risk]** Missing specific "Claude" or "Gemini" optimized hints → **[Mitigation]** Carefully merge critical environment-specific tips (like `just check` and `uv` sync rules) into the main `AGENTS.md`.
- **[Risk]** Context loss during cleanup → **[Mitigation]** Use a "Sync and Sweep" approach: verify all unique information is in `AGENTS.md` before deleting source files.
- **[Risk]** Maintenance overhead for Specs → **[Mitigation]** Keep initial specs high-level and focused on "Rules of the Road" (e.g., Dual-Party Confirmation) rather than granular implementation details.
