[< CV6 Multi-User Onboarding, Identity Runtime Maturity, and Extensibility](../index.md)

# CV6.E1 — Structured Identity Metadata in the Database

**Epic:** Runtime-relevant persona metadata is stored in the database rather than discarded at seed time  
**Status:** ✅ Done
**Prerequisite for:** CV6.E2

---

## What This Is

Today persona prompt content is stored in the database, but important runtime
metadata is not. In particular, fields such as `routing_keywords` live in the
seed YAML and are dropped during seeding. That means the database is not yet a
complete runtime source of truth for persona behavior.

This epic defines and lands the database-side identity metadata model needed for
runtime behavior such as persona routing, inspection, and future identity-aware
capabilities.

The core principle is explicit:

- seed YAML files are input to seeding
- the database is the runtime source of truth
- runtime persona routing must not depend on reading seed YAML files directly

---

## Done Condition

- runtime-relevant persona metadata has a defined structured representation in the database
- seeding persists that metadata instead of discarding it
- runtime code can inspect persona metadata through database-backed APIs
- docs clearly distinguish persona prompt content from persona metadata
- the metadata contract is explicit enough to support DB-backed persona routing in CV6.E2

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV6.E1.S1 | Define the runtime persona metadata contract | ✅ Done |
| CV6.E1.S2 | Implement database persistence and inspection for persona metadata | ✅ Done |

Completed in practice through database-backed persona metadata persistence,
seed-time metadata preservation, and inspection CLI support.

---

## Sequencing

```text
S1 (persona metadata contract)
  └── S2 (DB persistence and inspection)
```

The contract comes first. We should not implement routing or seeding changes
against an unclear storage model.

---

**See also:** [CV6](../index.md) · [CV6.E2 Persona Auto-Routing from Database Metadata](../cv6-e2-db-backed-persona-auto-routing/index.md)
