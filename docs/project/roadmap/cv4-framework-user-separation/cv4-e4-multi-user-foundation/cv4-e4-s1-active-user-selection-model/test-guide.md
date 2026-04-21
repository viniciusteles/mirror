[< CV4.E4.S1 Plan](plan.md)

# CV4.E4.S1 — Test Guide: Define the active-user selection model and conflict rules

## Scope

This story is planning/documentation only. No runtime implementation is in scope.

Verification is about confirming that the multi-user model is explicit and does
not depend on guessing or hidden single-user assumptions.

---

## Review Checklist

Confirm the docs clearly define:

1. **User-home model**
   - one isolated home per user under `~/.mirror/<user>/`

2. **Selection precedence**
   - CLI override
   - `MIRROR_HOME`
   - derived from `MIRROR_USER`
   - otherwise fail clearly

3. **Conflict rules**
   - conflicting `MIRROR_HOME` and `MIRROR_USER` values fail hard
   - missing selection fails hard
   - missing resolved home fails clearly

4. **Non-goals**
   - no automatic user picking by scanning `~/.mirror/`
   - no silent merge between user homes
   - no account/authentication system implied

5. **Architectural fit**
   - multi-user support remains aligned with CV4.E1 path rules
   - user homes remain isolated units for later operations

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/briefing.md`
- `docs/project/decisions.md`
- `docs/project/roadmap/cv4-framework-user-separation/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e1-user-home-layout/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e4-multi-user-foundation/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e4-multi-user-foundation/cv4-e4-s1-active-user-selection-model/plan.md`

Check specifically that the wording does **not** imply:
- auto-selection from existing directories
- a hidden default user
- authentication/accounts as part of CV4

---

## Validation Commands

```bash
rg -n "MIRROR_HOME|MIRROR_USER|~/.mirror/<user>|fail hard|scan|single-user|account" docs/project docs/process docs/index.md
```

Then run:

```bash
git diff --check
```

No runtime verification suite is required because no code behavior changes are in scope.
