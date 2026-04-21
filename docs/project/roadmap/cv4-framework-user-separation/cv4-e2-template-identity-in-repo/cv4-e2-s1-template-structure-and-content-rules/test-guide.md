[< CV4.E2.S1 Plan](plan.md)

# CV4.E2.S1 — Test Guide: Define the template identity structure and content rules

## Scope

This story is planning/documentation only. No runtime implementation is in scope.

Verification is about confirming that the template concept is defined clearly
enough to support later implementation without reintroducing personal identity
into the repo.

---

## Review Checklist

Confirm the docs clearly define:

1. **Template structure**
   - `templates/identity/`
   - subdirectories mirroring the user-home identity structure

2. **Allowed content**
   - placeholders
   - comments
   - generic examples only

3. **Disallowed content**
   - live personal identity
   - private biography/business/family context
   - anything runtime would mistake for a real user profile

4. **Language rule**
   - English-first templates
   - no new Portuguese domain naming

5. **Architectural separation**
   - repo templates are bootstrap assets only
   - real identity belongs in `~/.mirror/<user>/identity/`

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/briefing.md`
- `docs/project/decisions.md`
- `docs/project/roadmap/cv4-framework-user-separation/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e2-template-identity-in-repo/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e2-template-identity-in-repo/cv4-e2-s1-template-structure-and-content-rules/plan.md`

Check specifically that the wording does **not** blur:
- repo templates vs live identity
- generic examples vs personal examples
- bootstrap assets vs runtime source of truth

---

## Validation Commands

```bash
rg -n "templates/identity|live identity|bootstrap|real user identity|English-first" docs/project docs/process docs/index.md
```

Then run:

```bash
git diff --check
```

No runtime verification suite is required because no code behavior changes are in scope.
