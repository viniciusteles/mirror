[< CV4.E2.S2 Plan](plan.md)

# CV4.E2.S2 — Test Guide: Migration from repo-owned identity assumptions to `templates/identity/`

## Scope

This story is planning/documentation only. No runtime implementation is in scope.

Verification is about confirming that the migration plan is explicit enough to
avoid a naive file move from `identity/` to `templates/identity/`.

---

## Review Checklist

Confirm the docs clearly define:

1. **Current source material**
   - the current `identity/` tree is treated as migration source material, not final template content

2. **Classification framework**
   - generalize into template
   - replace with fresh template
   - remove from repo-owned identity

3. **High-risk files**
   - `self/soul.yaml`
   - `user/identity.yaml`
   - personalized personas
   - personalized journeys

4. **Migration principle**
   - preserve structure more aggressively than prose
   - avoid redaction theater
   - do not mechanically rename directories as if that solved the architecture

5. **Transition clarity**
   - current repo `identity/` assumptions are transitional
   - final target is `templates/identity/` for repo assets and `~/.mirror/<user>/identity/` for real identity

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/briefing.md`
- `docs/project/decisions.md`
- `docs/project/roadmap/cv4-framework-user-separation/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e2-template-identity-in-repo/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e2-template-identity-in-repo/cv4-e2-s1-template-structure-and-content-rules/plan.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e2-template-identity-in-repo/cv4-e2-s2-migration-from-repo-identity-assumptions/plan.md`

Check specifically that the wording does **not** imply:
- existing repo identity files can just be copied into templates unchanged
- redaction alone is sufficient to make a personal file generic
- transitional repo assumptions are part of the final architecture

---

## Validation Commands

```bash
rg -n "templates/identity|identity/|migration source material|redaction|generic template|real identity" docs/project docs/process docs/index.md
```

Then run:

```bash
git diff --check
```

No runtime verification suite is required because no code behavior changes are in scope.
