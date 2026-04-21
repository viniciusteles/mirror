[< CV5 Multisession Safety](../index.md)

# CV5.E2 — Concurrency Hardening

**Epic:** Concurrent access no longer corrupts runtime state or trips avoidable startup races  
**Status:** Done
**Prerequisite for:** CV5.E3

---

## What This Is

Moving runtime state into SQLite is necessary, but not sufficient. The new
control plane still has to behave correctly under real concurrent access.

This epic removes the remaining race-prone file update patterns and hardens
SQLite startup behavior so two sessions starting at the same time do not cause
lost updates or migration bookkeeping failures.

---

## Done Condition

- Session mapping no longer depends on read-modify-write JSON files
- Concurrent session creation is safe and covered by tests
- Database startup/migration bookkeeping does not fail under concurrent open
- Runtime code avoids unnecessary global mutable state for session routing

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV5.E2.S1 | Eliminate file-based session routing races | ✅ Done |
| CV5.E2.S2 | Make database startup safe under concurrent access | ✅ Done |

---

## Sequencing

```text
S1 (remove file races)
  └── S2 (safe db startup)
```

---

**See also:** [CV5.E1 Session-Scoped Runtime State](../cv5-e1-session-scoped-runtime-state/index.md)
