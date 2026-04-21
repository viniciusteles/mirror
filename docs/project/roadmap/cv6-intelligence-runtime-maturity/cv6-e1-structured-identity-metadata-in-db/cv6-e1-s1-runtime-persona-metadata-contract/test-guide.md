[< CV6.E1.S1 Plan](plan.md)

# CV6.E1.S1 — Test Guide: Define the runtime persona metadata contract

## Scope

This story is planning/documentation only. No runtime implementation is in scope.

Verification is about confirming that the docs define a clear database-backed
contract for runtime persona metadata and explicitly reject seed-YAML-dependent
runtime behavior.

---

## Review Checklist

Confirm the docs clearly define:

1. **Runtime source of truth**
   - persona routing metadata comes from the database
   - seed YAML is input to seeding, not a runtime dependency

2. **Minimum runtime metadata**
   - includes `routing_keywords`
   - distinguishes prompt content from metadata

3. **Storage direction**
   - proposes a concrete database storage direction
   - does not leave the representation fully implicit

4. **Routing dependency**
   - the contract is sufficient to enable DB-backed persona auto-routing

5. **Compatibility direction**
   - existing databases and current seed behavior are acknowledged explicitly

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/roadmap/index.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/index.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e1-structured-identity-metadata-in-db/index.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e1-structured-identity-metadata-in-db/cv6-e1-s1-runtime-persona-metadata-contract/plan.md`
- `REFERENCE.md`
- `CLAUDE.md`

Check specifically that the wording does **not** imply:
- runtime may read persona YAML files directly for routing
- `routing_keywords` can remain seed-only data indefinitely
- prompt body and metadata are the same thing operationally

---

## Validation Commands

```bash
rg -n "routing_keywords|source of truth|persona metadata|seed YAML|runtime" docs/project REFERENCE.md CLAUDE.md
```

Then run:

```bash
git diff --check
```

No runtime verification suite is required because no code behavior changes are in scope.
