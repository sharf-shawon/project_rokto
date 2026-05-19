## Context

The project enforces an uncompromisingly strict linting and code quality standard using Ruff (`A`, `ASYNC`, `B`, `BLE`, `C4`, `C90`, `COM`, `DJ`, `DTZ`, `E`, `EM`, `ERA`, `EXE`, `F`, `FA`, `FBT`, `FLY`, `G`, `I`, `ICN`, `INP`, `INT`, `ISC`, `N`, `PD`, `PERF`, `PGH`, `PIE`, `PL`, `PT`, `PTH`, `PYI`, `Q`, `RET`, `RSE`, `RUF`, `S`, `SIM`, `SLF`, `SLOT`, `T10`, `T20`, `TC`, `TID`, `TRY`, `UP`, `W`, `YTT`). AI agents naturally produce code that violates several of these advanced rules (e.g., Boolean positional arguments, blind exception passing, magic numbers). Instead of relying on a reactive workflow where the agent fails the CI checks and must auto-fix the issues, we need to inject these rules proactively into their primary context source (`openspec/specs/code-quality/spec.md`).

## Goals / Non-Goals

**Goals:**

- Provide clear, actionable, plain-English instructions inside the project's specification for AI agents.
- Translate the most frequent Ruff plugin violations (`FBT`, `TRY`, `EM`, `SIM`, `PLR`, `PLC`, `BLE`, `SLF`) into behavioral rules.
- Decrease the time and token consumption of the implementation phase by getting it right the first time.

**Non-Goals:**

- Changing any application code.
- Altering the `pyproject.toml` Ruff configuration to be more lenient.
- Replacing the reactive check (`just check`) — it remains the final line of defense.

## Decisions

- **Decision 1: Modify Existing Spec vs. New File.** We will modify the existing `openspec/specs/code-quality/spec.md` instead of creating a new `AI-RULES.md` or similar file. This ensures the rules are part of the standard OpenSpec capability mapping and read naturally during standard implementation.
- **Decision 2: Rule Mapping Strategy.** The new rules will be categorized logically (Exception Handling, Control Flow, Clean Code) rather than by Ruff code (e.g., `FBT001`). This makes it semantically understandable to LLMs.
- **Decision 3: Explicit Scenario Examples.** For complex rules (like exception handling), we will provide "Scenario" blocks in the spec to illustrate the required behavior, aligning with the existing BDD-style specification format.

## Risks / Trade-offs

- **Risk:** AI agents might still occasionally hallucinate violations if the context window overflows.
  **Mitigation:** The `just check` mandate remains the ultimate verification step, catching any edge cases the prompt injection misses.
- **Risk:** Maintaining sync between `pyproject.toml` and `spec.md`.
  **Mitigation:** The spec will focus on the idioms that AI historically struggles with, rather than exhaustively documenting every single Ruff rule.
