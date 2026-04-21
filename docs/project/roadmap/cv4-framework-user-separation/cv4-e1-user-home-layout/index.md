[< CV4 Framework/User Separation](../index.md)

# CV4.E1 — User Home Layout

**Epic:** Mirror Mind has a documented canonical per-user home under `~/.mirror/<user>/`  
**Status:** Done
**Prerequisite for:** CV4.E3, CV4.E4, CV4.E5, CV4.E6

---

## What This Is

CV4 needs a stable target before any loading, migration, multi-user selection,
or transcript export work can be implemented. That target is the per-user home.

This epic defines the canonical layout for one user's local Mirror Mind state:

```text
~/.mirror/<user>/
  identity/
    self/
    ego/
    user/
    organization/
    personas/
    journeys/
  memory.db
  backups/
  exports/
```

The point is not only to name folders. The point is to define ownership and
contract boundaries:
- what belongs in the repo vs. in the user home
- what paths are canonical vs. merely defaults
- what must be configurable
- how future features select and resolve the active user home

Without this contract, later epics would invent path behavior independently and
create another round of drift.

---

## Done Condition

- The canonical user-home layout is documented and accepted
- Path ownership is explicit for identity, runtime DB, backups, exports, and transcripts
- Configurable vs. non-configurable paths are clearly separated
- Path precedence rules are defined (defaults, env overrides, explicit flags if any)
- A first story defines the path contract tightly enough for implementation work to begin in CV4.E2–E6

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV4.E1.S1 | Define the user-home path contract and path precedence rules | ✅ Done |
| CV4.E1.S2 | Define default subdirectories and override policy for backups, exports, and transcripts | ✅ Done |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

## Sequencing

S1 should come first. The contract for path resolution and active-user selection
must exist before override policy is finalized.

```text
S1 (path contract and precedence)
  └── S2 (default subdirectories and override policy)
```

---

**See also:** [CV4 Framework/User Separation](../index.md) · [Briefing D3](../../../../project/briefing.md) · [Decisions](../../../../project/decisions.md)
