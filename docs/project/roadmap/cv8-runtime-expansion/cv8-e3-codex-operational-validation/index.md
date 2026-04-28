[< CV8 Runtime Expansion](../index.md)

# CV8.E3 — Codex Operational Validation & Docs

**Epic:** Prove the Codex runtime works end-to-end, does not touch production state during tests, and is documented honestly
**Status:** Draft
**Depends on:** CV8.E2 Codex Runtime Implementation

---

## What This Is

Runtime support is not done when files exist. It is done when the lifecycle has
been exercised against an isolated mirror home, the resulting database rows are
inspected, production state is proven untouched, and a new user can follow the
docs without relying on tribal knowledge.

This epic closes Codex as a supported runtime before any Gemini CLI work begins.

---

## Done Condition

- isolated Codex smoke test runs with temporary `HOME`, `MIRROR_HOME`, and
  `MEMORY_ENV=production`
- smoke test proves session start, user logging, assistant logging/backfill,
  session end, and backup behavior
- smoke test proves Mirror Mode context loading if Codex supports it
- smoke test proves Builder Mode command flow if Codex supports native commands
- resulting SQLite rows show `interface='codex'`
- production DB checksum or equivalent guard proves no production DB was touched
- README, Getting Started, REFERENCE, Runtime Interface Contract, and skill docs
  include Codex where appropriate
- Codex limitations are documented as limitations, not hidden in implementation
- worklog records Codex validation result and final parity level

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV8.E3.S1 | Write isolated Codex smoke test script | Draft |
| CV8.E3.S2 | Validate Codex session lifecycle end-to-end | Draft |
| CV8.E3.S3 | Validate Codex Mirror Mode and Builder Mode flows | Draft |
| CV8.E3.S4 | Update public and operational docs for Codex | Draft |
| CV8.E3.S5 | Record Codex parity level, limitations, and validation result | Draft |

---

## Verification Requirements

The final Codex validation must include at minimum:

```bash
uv run pytest
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run pyright src/memory
uv run git diff --check
```

Plus the Codex-specific isolated smoke test defined in S1.

---

## See also

- [CV8.E2 Codex Runtime Implementation](../cv8-e2-codex-runtime-implementation/index.md)
- [Development Guide](../../../process/development-guide.md)
