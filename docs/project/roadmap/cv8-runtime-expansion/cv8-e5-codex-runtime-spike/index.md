[< CV8 Runtime Expansion](../index.md)

# CV8.E5 — Codex Runtime Spike

**Epic:** Discover Codex's runtime model and map it against the Gemini CLI-hardened Mirror Mind runtime contract
**Status:** Draft
**Depends on:** CV8.E4 Runtime Adapter Hardening

---

## What This Is

Codex is the second new runtime in CV8. By this point Gemini CLI has already
forced one full pass through the runtime contract and the adapter hardening epic
has distilled the lessons. The Codex spike uses the improved contract and asks
the same hard questions:

- Can Codex expose lifecycle events?
- Can it capture user and assistant turns?
- Can it provide a stable session id?
- Can it inject Mirror Mode context before model response?
- Can it expose a native command or skill surface?

The output is a target parity level and an implementation plan. If Codex is less
capable than Gemini CLI, the integration is scoped accordingly. If it is more
capable, the runtime contract is updated again.

---

## Done Condition

- Codex documentation and local behavior are inspected
- Codex local project configuration shape is identified, if one exists
- Codex lifecycle events are mapped to the Gemini CLI-hardened runtime contract
- session id availability is confirmed or a deterministic fallback is designed
- prompt/assistant capture model is classified as per-turn events, transcript
  backfill, or unavailable
- context injection capability is classified as pre-response, command-only, or
  unavailable
- target parity level for Codex is selected using the CV8 parity table
- implementation constraints and risks are recorded before CV8.E6 begins

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| [CV8.E5.S1](cv8-e5-s1-codex-capabilities/index.md) | Inspect Codex extension, command, hook, and transcript capabilities | Draft |
| CV8.E5.S2 | Map Codex lifecycle to the runtime contract | Draft |
| CV8.E5.S3 | Decide Codex target parity level and document limitations | Draft |
| CV8.E5.S4 | Draft Codex implementation plan and test guide | Draft |

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

- [CV8.E4 Runtime Adapter Hardening](../cv8-e4-runtime-adapter-hardening/index.md)
- [CV8.E1 Gemini CLI Runtime Spike](../cv8-e1-gemini-cli-runtime-spike/index.md)
- [Runtime Interface Contract](../../../runtime-interface.md)
