[< CV2 Runtime Portability](../index.md)

# CV2.E3 — Runtime Interface Contract

**Epic:** The interface is documented; a new runtime could be built from it  
**Status:** ✅ Done  
**Prerequisite:** CV2.E1 and CV2.E2 complete

---

## What This Is

After E1 and E2, both runtimes call the same CLI commands for the same lifecycle
events. But nowhere is that contract written down. Adding a third runtime — a
Telegram bot, a web interface, a bare CLI — requires reading the source of both
existing implementations and inferring what's required.

This epic writes the runtime contract as a document. It describes what a runtime
must implement, what CLI commands map to each event, and how Claude Code and Pi
satisfy the contract. The document is the spec; the implementations are evidence
that the spec is correct.

---

## Done Condition

- `docs/project/runtime-interface.md` exists and fully describes:
  - The lifecycle events every runtime must handle (session start, user prompt,
    assistant response, session end)
  - The CLI command(s) to call for each event and their required arguments
  - Optional behaviors (mirror inject, UI notifications)
  - Claude Code (hooks) and Pi (extension) annotated as reference implementations
- The document is accurate against the actual code as of CV2.E1 + CV2.E2

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV2.E3.S1 | Write `docs/project/runtime-interface.md` | ✅ |

This story requires no plan.md or test-guide.md — it is documentation only.

---

**See also:** [CV2 Runtime Portability](../index.md) · [CV2.E1](../cv2-e1-session-lifecycle-parity/index.md) · [CV2.E2](../cv2-e2-hook-dispatch-to-cli/index.md)
