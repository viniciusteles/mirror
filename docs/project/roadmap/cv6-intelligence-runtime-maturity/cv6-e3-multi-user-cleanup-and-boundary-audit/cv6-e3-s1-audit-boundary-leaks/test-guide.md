[< CV6.E3.S1 Plan](plan.md)

# CV6.E3.S1 — Test Guide: Audit remaining repo/runtime/user-boundary leaks

## Scope

This story is planning/documentation only. No code migration is in scope.

Verification is about confirming that the audit identifies real boundary-leak
candidates, classifies them coherently, and creates a usable handoff into the
extension-model work.

---

## Review Checklist

Confirm the docs clearly identify and classify at least:

1. **Former repo-local personalized artifact**
   - the removed `engineer` meta persona is acknowledged as a resolved example of a boundary leak

2. **Extension candidate**
   - `.pi/skills/mm-review-copy/SKILL.md`
   - `.claude/skills/mm:review-copy/SKILL.md`

3. **Positive external-tool boundary example**
   - `financial-tools` references in docs

4. **Core runtime integration artifact**
   - `.pi/extensions/mirror-logger.ts`

5. **Classification vocabulary**
   - core framework feature
   - core runtime integration artifact
   - user-owned identity
   - repo-local development artifact
   - external/user-installed extension

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/roadmap/cv6-intelligence-runtime-maturity/index.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e3-multi-user-cleanup-and-boundary-audit/index.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e3-multi-user-cleanup-and-boundary-audit/cv6-e3-s1-audit-boundary-leaks/plan.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/index.md`
- `README.md`
- `REFERENCE.md`

Check specifically that the wording does **not** imply:
- every repo-local artifact is automatically a framework bug
- Pi runtime integration artifacts are the same thing as user-specific extensions
- `review-copy` is already settled as core
- removed repo-local personalized artifacts still belong to the user-home seed/runtime identity model

---

## Validation Commands

```bash
rg -n "financial-tools|review-copy|mirror-logger|extension|user-specific|repo-local" README.md REFERENCE.md docs .pi .claude
```

Then run:

```bash
git diff --check
```

No runtime verification suite is required because no code behavior changes are in scope.
