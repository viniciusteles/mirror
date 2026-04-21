[< CV4 Framework/User Separation](../index.md)

# CV4.E5 — Legacy Migration into User Home

**Epic:** Old Portuguese-era data migrates into the new user-home layout  
**Status:** Done
**Prerequisite for:** implementation after CV4.E1–E4 direction is stable

---

## What This Is

CV4 establishes a new architecture:
- user homes under `~/.mirror/<user>/`
- user-owned identity under `identity/`
- runtime state centered on `memory.db`

But existing Mirror Mind data may still exist in older forms, especially from
the Portuguese-era architecture:
- `memoria.db`
- Portuguese schema/value names like `travessia`
- older path and repo-root assumptions

This epic plans how that legacy state migrates explicitly into the new user-home
model instead of being left behind or silently reinterpreted.

This is not just a schema translation problem. It is a source/target contract,
operational safety, and architectural cleanup problem.

Current state: the project now has an explicit `migrate-legacy validate` /
`migrate-legacy run` workflow for clean Portuguese-era databases, with JSON
report output and post-migration verification. That closes the core user-home
migration path required by CV4.

---

## Done Condition

- Legacy migration inputs and outputs are defined clearly
- Migration targets the user-home architecture under `~/.mirror/<user>/`
- Schema/data vocabulary translation is planned explicitly
- Migration is user-scoped, explicit, and safe by default
- Follow-on implementation stories are clear enough to build and verify the migration path deliberately

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV4.E5.S1 | Define the migration source/target contract and safety rules | ✅ Done |
| CV4.E5.S2 | Plan legacy schema and vocabulary translation into `memory.db` | ✅ Done |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

## Sequencing

S1 comes first. We need to define what is being migrated, where it goes, and
how explicit/safe the operation is before planning translation mechanics.

```text
S1 (source/target contract and safety)
  └── S2 (schema and vocabulary translation)
```

---

**See also:** [CV4 Framework/User Separation](../index.md) · [CV4.E1 User Home Layout](../cv4-e1-user-home-layout/index.md) · [CV4.E3 External Identity Loading and Seeding](../cv4-e3-external-identity-loading-and-seeding/index.md)
