[< CV5 Multisession Safety](../index.md)

# CV5.E3 — Runtime Integration and Validation

**Epic:** Claude Code and Pi flows use the safer session model and have regression coverage for simultaneous use  
**Status:** Done

---

## What This Is

Once the core session model is safe, the runtimes need to use it explicitly.
Claude Code hooks already receive `session_id` in their hook payloads. Pi
extensions already have a stable session file path. Those integrations should
stop depending on singleton runtime files where explicit session identifiers are
already available.

This epic wires the safer model into the runtimes and proves it with focused
regression coverage.

---

## Done Condition

- Claude hooks pass explicit session ids to the session-aware runtime helpers
- Pi runtime logging uses explicit session ids end-to-end where available
- Tests cover independent mirror state across sessions and concurrent session creation
- Docs and operational guidance reflect the new multisession model

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV5.E3.S1 | Plumb explicit session ids through Claude hook flows | ✅ Done |
| CV5.E3.S2 | Validate runtime behavior and add multisession regression coverage | ✅ Done |

---

## Sequencing

```text
S1 (runtime plumbing)
  └── S2 (validation and regression coverage)
```

---

**See also:** [CV5.E2 Concurrency Hardening](../cv5-e2-concurrency-hardening/index.md)
