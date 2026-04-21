[< Roadmap](../index.md)

# CV5 — Multisession Safety

**Status:** Done
**Goal:** Make one mirror home safe for simultaneous sessions by replacing singleton runtime state with session-scoped state, moving session mapping into SQLite, and hardening startup/runtime flows against concurrency.

---

## What This Is

CV4 made Mirror Mind multi-user at the user-home level. But within a single
mirror home, runtime control still assumes one active session at a time.
Global files such as `current_session`, `mirror_state.json`, and
`session_map.json` create race conditions and cross-session contamination.

CV5 turns multisession safety into a first-class capability:
- session ↔ conversation mapping becomes database-backed and concurrency-safe
- mirror activation state becomes session-scoped rather than home-scoped
- runtime hooks/extensions pass explicit session ids where they already have them
- startup and migration logic tolerate concurrent access cleanly
- regression coverage includes concurrent session behavior rather than only
  sequential single-session flows

This CV intentionally defers intelligence-depth work to CV6. Safety of the
runtime control plane comes first.

---

## Epics

| Code | Epic | User-visible outcome | Status |
|------|------|----------------------|--------|
| [CV5.E1](cv5-e1-session-scoped-runtime-state/index.md) | Session-Scoped Runtime State | Active session behavior no longer depends on singleton files | ✅ Done |
| [CV5.E2](cv5-e2-concurrency-hardening/index.md) | Concurrency Hardening | Concurrent access no longer corrupts runtime state or trips avoidable startup races | ✅ Done |
| [CV5.E3](cv5-e3-runtime-integration-and-validation/index.md) | Runtime Integration and Validation | Claude Code and Pi flows use the safer session model and have regression coverage for simultaneous use | ✅ Done |

---

## Done Condition

CV5 is done when:
- one mirror home can host more than one simultaneous active runtime session
- session ↔ conversation binding is stored transactionally in SQLite
- mirror mode state is session-scoped for runtimes that provide a session id
- no critical runtime flow depends on overwriting a singleton session file
- concurrent startup no longer fails due to migration bookkeeping races
- tests demonstrate safe concurrent session creation and independent session state
- docs describe the new multisession contract clearly

---

## Sequencing

```text
E1 (session-scoped runtime state)
  └── E2 (concurrency hardening)
        └── E3 (runtime integration and validation)
```

E1 establishes the new control-plane model. E2 hardens it under concurrent
access. E3 updates runtime integrations and locks the behavior in with tests.

---

## Out of Scope

- extraction prompt tuning
- shadow-layer activation work
- hybrid search weighting changes
- reinforcement score tuning

Those move to CV6.

---

**See also:** [Roadmap](../index.md) · [Decisions](../../decisions.md) · [Worklog](../../../process/worklog.md)
