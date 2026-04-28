[< CV8 Runtime Expansion](../index.md)

# CV8.E5 — Gemini CLI Runtime Spike

**Epic:** Discover Gemini CLI's runtime model and map it against the Codex-hardened Mirror Mind runtime contract
**Status:** Draft
**Depends on:** CV8.E4 Runtime Adapter Hardening

---

## What This Is

Gemini CLI is the second new runtime in CV8. It should not start from a blank
page. By this point Codex has already forced one full pass through the runtime
contract. The Gemini spike uses that improved contract and asks the same hard
questions:

- Can Gemini CLI expose lifecycle events?
- Can it capture user and assistant turns?
- Can it provide a stable session id?
- Can it inject Mirror Mode context before model response?
- Can it expose a native command surface?

The output is a target parity level and an implementation plan. If Gemini CLI is
less capable than Codex, the integration is scoped accordingly. If it is more
capable, the runtime contract is updated again.

---

## Done Condition

- Gemini CLI documentation and local behavior are inspected
- Gemini CLI local project configuration shape is identified, if one exists
- Gemini CLI lifecycle events are mapped to the Codex-hardened runtime contract
- session id availability is confirmed or a deterministic fallback is designed
- prompt/assistant capture model is classified as per-turn events, transcript
  backfill, or unavailable
- context injection capability is classified as pre-response, command-only, or
  unavailable
- target parity level for Gemini CLI is selected using the CV8 parity table
- implementation constraints and risks are recorded before CV8.E6 begins

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV8.E5.S1 | Inspect Gemini CLI extension, command, hook, and transcript capabilities | Draft |
| CV8.E5.S2 | Map Gemini CLI lifecycle to the runtime contract | Draft |
| CV8.E5.S3 | Decide Gemini CLI target parity level and document limitations | Draft |
| CV8.E5.S4 | Draft Gemini CLI implementation plan and test guide | Draft |

---

## Key Questions

- Where does Gemini CLI read project-local commands or instructions from?
- Can Gemini CLI run shell commands automatically on lifecycle events?
- Can Gemini CLI observe the user prompt before model execution?
- Can Gemini CLI observe the assistant response after model execution?
- Does Gemini CLI provide a stable session id?
- Does Gemini CLI expose a transcript file path?
- Can Gemini CLI inject a system/context block before the model responds?
- Can Gemini CLI discover runtime-provided skills dynamically, or only static
  command files?

---

## See also

- [CV8.E4 Runtime Adapter Hardening](../cv8-e4-runtime-adapter-hardening/index.md)
- [Runtime Interface Contract](../../../runtime-interface.md)
