[< CV5 Multisession Safety](../index.md)

# CV5.E1 — Session-Scoped Runtime State

**Epic:** Active session behavior no longer depends on singleton files  
**Status:** Done
**Prerequisite for:** CV5.E2

---

## What This Is

Today the control plane for Mirror Mind is split between the database and a set
of singleton files under the mirror home. That model breaks down when more than
one session is active at the same time.

This epic moves the authoritative runtime state into the database, keyed by
runtime `session_id`. The database already stores conversations; now it also
needs to store which runtime session owns which conversation and what mirror
mode state applies to that session.

---

## Done Condition

- Session ↔ conversation mapping is database-backed
- Mirror mode state is session-scoped instead of global
- Core logging and mirror commands can target a specific session explicitly
- Legacy singleton files are no longer authoritative for session routing

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV5.E1.S1 | Introduce a runtime session registry in SQLite | ✅ Done |
| CV5.E1.S2 | Move mirror state and conversation routing to session-scoped storage | ✅ Done |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

## Sequencing

```text
S1 (runtime session registry)
  └── S2 (session-scoped mirror state and routing)
```

---

**See also:** [CV5 Multisession Safety](../index.md) · [CV5.E2 Concurrency Hardening](../cv5-e2-concurrency-hardening/index.md)
