[< CV6.E5.S4 Plan](plan.md)

# CV6.E5.S4 — Test Guide: Migrate `review-copy` to the external skill model

## Scope

This story is planning/documentation only. No runtime migration is in scope yet.

Verification is about confirming that there is now a credible migration target
for the first real external skill.

---

## Review Checklist

Confirm the docs clearly define:

1. **Target location**
   - user-home external extension directory

2. **Target naming**
   - explicit external skill namespace

3. **Migration phases**
   - parallel reference form
   - preferred external form
   - eventual removal/archive of in-repo reference form

4. **Contract discipline**
   - stable core commands instead of private internal imports

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/cv6-e5-s2-review-copy-reference-path/plan.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/cv6-e5-s3-external-skill-registry-and-manifest-contract/plan.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/cv6-e5-s4-migrate-review-copy-to-external-skill-model/plan.md`
- `.pi/skills/mm-review-copy/SKILL.md`
- `.claude/skills/mm:review-copy/SKILL.md`

Check specifically that the wording does **not** imply:
- `review-copy` should stay permanently in the core repo surface
- migration can happen before the external discovery model exists
- the external version should depend on private Mirror internals

---

## Validation Commands

```bash
rg -n "review-copy|ext:review-copy|ext-review-copy|extensions/review-copy|skill.yaml" docs/project .pi .claude
```

Then run:

```bash
git diff --check
```

No runtime verification suite is required because no code behavior changes are in scope.
