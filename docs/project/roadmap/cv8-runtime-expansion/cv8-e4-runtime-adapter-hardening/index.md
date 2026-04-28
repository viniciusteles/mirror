[< CV8 Runtime Expansion](../index.md)

# CV8.E4 — Runtime Adapter Hardening

**Epic:** Fold Codex lessons back into the shared runtime contract before starting Gemini CLI
**Status:** Draft
**Depends on:** CV8.E3 Codex Operational Validation & Docs

---

## What This Is

Codex is the first new runtime after Pi. It will expose assumptions in our
runtime contract: naming, session-id handling, command surfaces, smoke-test
patterns, docs structure, and maybe gaps in `conversation-logger` ergonomics.

This epic prevents duplication. Before implementing Gemini CLI, we harvest what
Codex taught us and turn it into reusable adapter guidance, tests, helpers, or
docs. The goal is not premature abstraction; it is not making Gemini repeat the
same discovery work.

---

## Done Condition

- Codex implementation is reviewed for patterns that should become generic
- `docs/project/runtime-interface.md` reflects any contract refinements learned
  from Codex
- recurring smoke-test setup is extracted into reusable shell/Python helpers if
  duplication is already visible
- runtime naming conventions are documented (`claude_code`, `pi`, `codex`,
  future `gemini_cli`)
- command surface expectations are documented in one place
- any Python CLI affordances needed by non-Claude/non-Pi runtimes are added
  before Gemini work starts
- no unnecessary abstraction is introduced without a second concrete use case

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV8.E4.S1 | Review Codex adapter for reusable runtime patterns and design debt | Draft |
| CV8.E4.S2 | Update Runtime Interface Contract with Codex-tested refinements | Draft |
| CV8.E4.S3 | Extract reusable isolated-smoke-test helpers if justified | Draft |
| CV8.E4.S4 | Standardize runtime interface labels and reporting language | Draft |
| CV8.E4.S5 | Prepare Gemini CLI implementation checklist from Codex lessons | Draft |

---

## Guardrail

Do not build a generic runtime framework in the abstract. Extract only what
Codex made concrete and Gemini is about to reuse. The principle is:

> Two runtimes justify a pattern. One runtime justifies a note.

---

## See also

- [CV8.E3 Codex Operational Validation & Docs](../cv8-e3-codex-operational-validation/index.md)
- [Runtime Interface Contract](../../../runtime-interface.md)
- [Principles](../../../product/principles.md)
