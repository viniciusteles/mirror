[< CV2 Runtime Portability](../index.md)

# CV2.E1 — Session Lifecycle Parity

**Epic:** Both runtimes handle session start/end identically  
**Status:** ✅ Done  
**Parallel with:** CV2.E2

---

## What This Is

Pi's `session_start` handler calls `python -m memory conversation-logger session-start`,
which does three things: unmute, close stale orphan conversations, and extract
pending memories.

Claude Code's `session-start.sh` only unmutes. Orphan closing and pending
extraction never happen in a Claude Code session.

This is a behavioral gap. A conversation opened in Pi and abandoned may leave
an orphan that only Pi will clean up. Pending memory extraction only fires when
Pi starts, never when Claude Code starts.

This epic aligns Claude Code's session-start hook to call the same CLI command
as Pi, so both runtimes produce identical session lifecycle behavior.

---

## Done Condition

- `session-start.sh` calls `python -m memory conversation-logger session-start`
  (same command Pi uses)
- `log-session-end.sh` calls `python -m memory conversation-logger session-end-pi`
  or an equivalent unified CLI command
- Session start and end behavior is identical across both runtimes
- Existing tests pass; new tests cover the unified session-start path

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV2.E1.S1 | Align `session-start.sh` to call the unified CLI command | ✅ |
| CV2.E1.S2 | Align `log-session-end.sh` to call the unified CLI command | ✅ |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

**See also:** [CV2 Runtime Portability](../index.md) · [CV2.E2 Hook Dispatch to CLI](../cv2-e2-hook-dispatch-to-cli/index.md)
