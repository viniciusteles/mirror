[< CV8 Runtime Expansion](../index.md)

# CV8.E7 — Gemini CLI Operational Validation & Docs

**Epic:** Prove the Gemini CLI runtime works end-to-end, does not touch production state during tests, and is documented honestly
**Status:** Draft
**Depends on:** CV8.E6 Gemini CLI Runtime Implementation

---

## What This Is

This epic closes Gemini CLI support and therefore closes CV8. The validation
standard is the same as Codex: isolated runtime execution, inspected database
rows, production-state safety, and complete docs.

Because Gemini CLI comes after Codex, this epic also verifies whether the runtime
adapter hardening actually reduced duplication and made the second runtime easier
to add.

---

## Done Condition

- isolated Gemini CLI smoke test runs with temporary `HOME`, `MIRROR_HOME`, and
  `MEMORY_ENV=production`
- smoke test proves session start, user logging, assistant logging/backfill,
  session end, and backup behavior
- smoke test proves Mirror Mode context loading if Gemini CLI supports it
- smoke test proves Builder Mode command flow if Gemini CLI supports native
  commands
- resulting SQLite rows show `interface='gemini_cli'`
- production DB checksum or equivalent guard proves no production DB was touched
- README, Getting Started, REFERENCE, Runtime Interface Contract, and skill docs
  include Gemini CLI where appropriate
- Gemini CLI limitations are documented as limitations, not hidden in
  implementation
- worklog records Gemini CLI validation result and final parity level
- CV8 index is updated from Draft/In Progress to Done when all epics close

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV8.E7.S1 | Write isolated Gemini CLI smoke test script | Draft |
| CV8.E7.S2 | Validate Gemini CLI session lifecycle end-to-end | Draft |
| CV8.E7.S3 | Validate Gemini CLI Mirror Mode and Builder Mode flows | Draft |
| CV8.E7.S4 | Update public and operational docs for Gemini CLI | Draft |
| CV8.E7.S5 | Record Gemini CLI parity level, limitations, and validation result | Draft |
| CV8.E7.S6 | Close CV8 roadmap and worklog | Draft |

---

## Verification Requirements

The final Gemini CLI validation must include at minimum:

```bash
uv run pytest
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run pyright src/memory
uv run git diff --check
```

Plus the Gemini CLI-specific isolated smoke test defined in S1.

---

## See also

- [CV8.E6 Gemini CLI Runtime Implementation](../cv8-e6-gemini-cli-runtime-implementation/index.md)
- [Development Guide](../../../process/development-guide.md)
