## 1. Cleanup Redundant Files

- [x] 1.1 Delete redundant `CODEX.md` from the root directory.
- [x] 1.2 Delete `COPILOT-INSTRUCTIONS.md` from the root directory.
- [x] 1.3 Delete misleading `.github/COOKIE-CUTTER-AGENT.md`.

## 2. Consolidate Core Instructions (AGENTS.md)

- [x] 2.1 Update `AGENTS.md` to formally include the OpenSpec `/opsx:*` workflow commands.
- [x] 2.2 Merge critical developer environment notes (just, uv, pytest) into `AGENTS.md` from other loaders.
- [x] 2.3 Refine the "Development Lifecycle" section in `AGENTS.md` to align with OpenSpec phases.

## 3. Update AI Agent Loaders

- [x] 3.1 Update `GEMINI.md` to be a minimal loader pointing to `AGENTS.md` and enforcing `/opsx:*` usage.
- [x] 3.2 Update `CLAUDE.md` to be a minimal loader pointing to `AGENTS.md`.

## 4. Bootstrap OpenSpec Main Specs

- [x] 4.1 Ensure `openspec/specs/` directory exists.
- [x] 4.2 Finalize the initial specs in the change directory: `ai-onboarding`, `blood-request-lifecycle`, and `donor-privacy-security`.
- [ ] 4.3 (Post-Archive) Verify that `openspec/specs/` contains the consolidated foundational requirements.
