## Why

The current repository contains fragmented and redundant AI instruction files (e.g., `CODEX.md`, `COPILOT-INSTRUCTIONS.md`, `GEMINI.md`) that create confusion for AI agents. Additionally, `.github/COOKIE-CUTTER-AGENT.md` contains misleading instructions related to the project's source template rather than the application itself. Consolidation is needed to establish a single source of truth (SSoT) and formalize the development workflow using OpenSpec.

## What Changes

- **Removal**: Delete redundant and misleading AI instruction files: `CODEX.md`, `COPILOT-INSTRUCTIONS.md`, and `.github/COOKIE-CUTTER-AGENT.md`.
- **Consolidation**: Update `AGENTS.md` to be the primary SSoT for all AI agents, incorporating relevant context from the deleted files and the new OpenSpec workflow.
- **Workflow Formalization**: Update `GEMINI.md` to strictly follow the Project Rokto OpenSpec workflow (`/opsx:*`).
- **Foundational Specs**: Bootstrap initial technical specifications for core system boundaries to guide future AI implementations.

## Capabilities

### New Capabilities

- `ai-onboarding`: Standardized instructions, coding conventions, and workflow rules for AI agents.
- `blood-request-lifecycle`: Functional requirements for blood requests, donor matching, and dual-party confirmation.
- `donor-privacy-security`: Security boundaries and privacy rules for contact information exchange and NID verification.

### Modified Capabilities

<!-- None -->

## Impact

- **Documentation**: Significant cleanup of root-level and `.github/` markdown files.
- **AI Agent Context**: Improved accuracy and reduced token waste by providing a single, coherent set of instructions.
- **Project Structure**: Initialization of `openspec/specs/` with foundational requirement documents.
