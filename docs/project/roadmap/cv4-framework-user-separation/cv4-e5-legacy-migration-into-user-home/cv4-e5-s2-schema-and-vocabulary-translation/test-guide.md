[< CV4.E5.S2 Plan](plan.md)

# CV4.E5.S2 — Test Guide: Legacy schema and vocabulary translation into `memory.db`

## Scope

This story is planning/documentation only. No runtime implementation is in scope.

Verification is about confirming that the migration plan treats schema/value
translation as a semantic migration problem, not a naive rename exercise.

---

## Review Checklist

Confirm the docs clearly define:

1. **Translation scope**
   - `memoria.db` → `memory.db`
   - `travessia` → `journey`
   - `travessia_id` → `journey_id`
   - `caminho` → `journey_path`
   - related schema/index/layer mappings

2. **Translation principles**
   - preserve meaning, not just spelling
   - preserve data where possible
   - characterize realistic legacy sources first

3. **Verification depth**
   - row counts alone are not enough
   - indexes, layer values, and relationship behavior matter

4. **Mixed-state handling**
   - mixed or partially migrated legacy inputs are treated explicitly, not accidentally

5. **Architectural separation**
   - translation logic is distinguished from source/destination safety logic

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/english-domain-language-migration-plan.md`
- `docs/portuguese-domain-language-inventory.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e5-legacy-migration-into-user-home/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e5-legacy-migration-into-user-home/cv4-e5-s1-migration-source-target-contract-and-safety/plan.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e5-legacy-migration-into-user-home/cv4-e5-s2-schema-and-vocabulary-translation/plan.md`

Check specifically that the wording does **not** imply:
- migration is only table/column renaming
- row-count equality alone proves correctness
- mixed legacy states will be handled implicitly without a stated policy

---

## Validation Commands

```bash
rg -n "travessia|journey|travessia_id|journey_id|caminho|journey_path|memoria.db|memory.db" docs/project docs/process docs/*.md src/memory
```

Then run:

```bash
git diff --check
```

No runtime verification suite is required because no code behavior changes are in scope.
