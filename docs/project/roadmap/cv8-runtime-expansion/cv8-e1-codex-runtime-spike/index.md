[< CV8 Runtime Expansion](../index.md)

# CV8.E1 — Codex Runtime Spike

**Epic:** Discover Codex's runtime model and map it honestly against the Mirror Mind runtime contract
**Status:** Draft
**Depends on:** Existing runtime contract, Claude Code and Pi reference implementations

---

## What This Is

Before writing a Codex adapter, we need to know what Codex actually exposes. The
central question is not "can we call Python from Codex?" The central question is
whether Codex can satisfy Mirror Mind's runtime lifecycle:

- session start
- user prompt logging
- assistant response logging or transcript backfill
- session end
- backup
- Mirror Mode pre-response context injection
- native command/skill surface

This spike produces the decision record that constrains the implementation. If
Codex supports hooks and context injection, we target full runtime parity. If it
only supports explicit commands, we target command-level integration and document
that automatic Mirror Mode is not available.

---

## Done Condition

- Codex documentation and local behavior are inspected
- Codex local project configuration shape is identified, if one exists
- Codex lifecycle events are mapped to `docs/project/runtime-interface.md`
- session id availability is confirmed or a deterministic fallback is designed
- prompt/assistant capture model is classified as per-turn events, transcript
  backfill, or unavailable
- context injection capability is classified as pre-response, command-only, or
  unavailable
- target parity level for Codex is selected using the CV8 parity table
- implementation constraints and risks are recorded before CV8.E2 begins

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV8.E1.S1 | Inspect Codex extension, command, hook, and transcript capabilities | Draft |
| CV8.E1.S2 | Map Codex lifecycle to the Mirror runtime contract | Draft |
| CV8.E1.S3 | Decide Codex target parity level and document limitations | Draft |
| CV8.E1.S4 | Draft Codex implementation plan and test guide | Draft |

---

## Key Questions

- Where does Codex read project-local commands or instructions from?
- Can Codex run shell commands automatically on lifecycle events?
- Can Codex observe the user prompt before model execution?
- Can Codex observe the assistant response after model execution?
- Does Codex provide a stable session id?
- Does Codex expose a transcript file path?
- Can Codex inject a system/context block before the model responds?
- Can Codex discover runtime-provided skills dynamically, or only static command
  files?

---

## See also

- [CV8 index](../index.md)
- [Runtime Interface Contract](../../../runtime-interface.md)
