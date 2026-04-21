[< CV4.E4.S2 Plan](plan.md)

# CV4.E4.S2 — Test Guide: Define multi-user-safe behavior for user-scoped operations

## Scope

This story is planning/documentation only. No runtime implementation is in scope.

Verification is about confirming that user-scoped operations are defined as
single-home operations and do not allow implicit cross-user behavior.

---

## Review Checklist

Confirm the docs clearly define:

1. **Single-home targeting**
   - one invocation targets one resolved user home

2. **Scoped outputs**
   - backups, transcript exports, and similar artifacts remain scoped to the active user unless explicitly overridden

3. **No implicit cross-user work**
   - no operation runs across multiple homes by default
   - no hidden merge between user homes

4. **Operation-specific direction**
   - seed
   - backup
   - transcript export
   - migration/import
   are each described as user-scoped operations

5. **Failure/output clarity**
   - error messages and relevant outputs should identify the targeted user home clearly

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/briefing.md`
- `docs/project/decisions.md`
- `docs/project/roadmap/cv4-framework-user-separation/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e4-multi-user-foundation/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e4-multi-user-foundation/cv4-e4-s1-active-user-selection-model/plan.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e4-multi-user-foundation/cv4-e4-s2-multi-user-safe-operations/plan.md`

Check specifically that the wording does **not** imply:
- commands operate on all users by default
- backup/export/migration may silently cross user boundaries
- bulk multi-user orchestration is part of the default CV4 command model

---

## Validation Commands

```bash
rg -n "single-home|multi-user|backup|transcript export|migration|user-scoped|cross-user" docs/project docs/process docs/index.md
```

Then run:

```bash
git diff --check
```

No runtime verification suite is required because no code behavior changes are in scope.
