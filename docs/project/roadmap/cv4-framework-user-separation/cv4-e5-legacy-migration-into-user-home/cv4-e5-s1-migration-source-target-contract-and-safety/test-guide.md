[< CV4.E5.S1 Plan](plan.md)

# CV4.E5.S1 — Test Guide: Define the migration source/target contract and safety rules

## Scope

This story is planning/documentation only. No runtime implementation is in scope.

Verification is about confirming that the migration path is framed as an explicit,
user-scoped, safety-first operation rather than a vague conversion script.

---

## Review Checklist

Confirm the docs clearly define:

1. **Legacy source**
   - old Portuguese-era DB (for example `memoria.db`) is explicit input

2. **Destination**
   - one explicit user home under `~/.mirror/<user>/`
   - target runtime DB is `memory.db`

3. **User scoping**
   - one migration run targets one destination home only

4. **Safety rules**
   - no in-place mutation of source
   - no silent merge into destination
   - no hidden startup migration
   - validation/reporting are part of the normal path

5. **Architectural fit**
   - migration aligns with CV4 user-home architecture
   - migration is not just schema renaming in isolation

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/briefing.md`
- `docs/project/decisions.md`
- `docs/project/roadmap/cv4-framework-user-separation/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e5-legacy-migration-into-user-home/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e5-legacy-migration-into-user-home/cv4-e5-s1-migration-source-target-contract-and-safety/plan.md`

Check specifically that the wording does **not** imply:
- migration is just a one-off rename script with no operational contract
- source may be mutated in place
- target user home may be guessed implicitly
- migration is hidden inside normal startup/runtime behavior

---

## Validation Commands

```bash
rg -n "memoria.db|memory.db|~/.mirror/<user>|migration|source|destination|report|safety" docs/project docs/process docs/index.md
```

Then run:

```bash
git diff --check
```

No runtime verification suite is required because no code behavior changes are in scope.
