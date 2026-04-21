[< CV6 Multi-User Onboarding, Identity Runtime Maturity, and Extensibility](../index.md)

# CV6.E2 — Persona Auto-Routing from Database Metadata

**Epic:** Mirror Mode can resolve personas from database-backed routing metadata instead of relying only on explicit or sticky persona state  
**Status:** Planned
**Prerequisite for:** CV6.E3, CV6.E4

---

## What This Is

Today Mirror Mode can resolve a persona only through explicit input or sticky
runtime defaults. It can auto-detect journeys, but not personas. Even worse,
`routing_keywords` are not preserved as runtime metadata in the database, so the
system cannot perform proper persona routing from database state alone.

This epic introduces DB-backed persona auto-routing. Once CV6.E1 defines and
persists runtime persona metadata, Mirror Mode should be able to detect the most
likely persona from the user's query without reading seed YAML files.

---

## Done Condition

- Mirror Mode can detect personas from the query using database-backed persona metadata
- runtime persona detection does not read persona YAML files directly
- persona resolution order is explicit and tested
- no-match behavior falls back cleanly to ego/no-persona
- CLI/runtime behavior makes detected persona selection inspectable enough to debug

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV6.E2.S1 | Define the persona auto-routing contract and scoring rules | Planned |
| CV6.E2.S2 | Implement DB-backed persona detection in Mirror Mode | Planned |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

## Sequencing

```text
S1 (routing contract and scoring rules)
  └── S2 (Mirror Mode implementation)
```

We should agree on precedence and matching behavior before changing runtime
resolution logic.

---

**See also:** [CV6](../index.md) · [CV6.E1 Structured Identity Metadata in the Database](../cv6-e1-structured-identity-metadata-in-db/index.md)
