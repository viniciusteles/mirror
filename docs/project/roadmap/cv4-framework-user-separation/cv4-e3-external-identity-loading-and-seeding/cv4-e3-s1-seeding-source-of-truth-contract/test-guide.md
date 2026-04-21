[< CV4.E3.S1 Plan](plan.md)

# CV4.E3.S1 — Test Guide: Define the seeding source-of-truth contract for user-home identity

## Scope

This story is planning/documentation only. No runtime implementation is in scope.

Verification is about confirming that the seeding contract is explicit enough to
break the old repo-root identity assumption without blurring bootstrap and runtime.

---

## Review Checklist

Confirm the docs clearly define:

1. **Seeding source of truth**
   - `~/.mirror/<user>/identity/`

2. **Template role**
   - `templates/identity/` is bootstrap-only
   - templates are not runtime seed input

3. **Resolution contract**
   - seeding follows the CV4.E1 user-home resolution model

4. **Failure behavior**
   - required core identity is explicit: `self/`, `ego/`, `user/`
   - optional sections are explicit: `organization/`, `personas/`, `journeys/`
   - missing required core identity fails clearly
   - no silent fallback to repo identity or templates

5. **Separation of concerns**
   - bootstrap creates/copies identity structure
   - seeding loads user-owned identity into the database

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/briefing.md`
- `docs/project/decisions.md`
- `docs/project/roadmap/cv4-framework-user-separation/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e1-user-home-layout/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e2-template-identity-in-repo/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e3-external-identity-loading-and-seeding/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e3-external-identity-loading-and-seeding/cv4-e3-s1-seeding-source-of-truth-contract/plan.md`

Check specifically that the wording does **not** imply:
- repo `identity/` is still the intended long-term seed source
- templates may be used as implicit runtime seed input
- bootstrap and seeding are interchangeable operations

---

## Validation Commands

```bash
rg -n "seed|templates/identity|~/.mirror/<user>/identity|bootstrap|repo identity" docs/project docs/process docs/index.md
```

Then run:

```bash
git diff --check
```

No runtime verification suite is required because no code behavior changes are in scope.
