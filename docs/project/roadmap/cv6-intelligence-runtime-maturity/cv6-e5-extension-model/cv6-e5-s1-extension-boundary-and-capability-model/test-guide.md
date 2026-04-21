[< CV6.E5.S1 Plan](plan.md)

# CV6.E5.S1 — Test Guide: Define the extension boundary and capability model

## Scope

This story is planning/documentation only. No extension runtime implementation is in scope.

Verification is about confirming that the docs define a clear boundary model for
core features, user-owned identity, runtime integrations, and user-specific
extensions.

---

## Review Checklist

Confirm the docs clearly define:

1. **Core framework features**
   - identity/memory/journeys/runtime control-plane capabilities remain core

2. **User-owned identity**
   - personas, journeys, and user-authored identity remain user-owned/runtime-seeded

3. **Core runtime integration artifacts**
   - Pi lifecycle integration is distinguished from user-specific extensions

4. **Extension model**
   - preferred integration is through CLI/API/files/attachments/custom skills
   - arbitrary in-process plugin loading is not the default direction

5. **Current example classification**
   - `financial-tools`
   - `review-copy`
   - X digest / `xdigest`

6. **Follow-on path**
   - `review-copy` is identified as the first likely reference migration/example

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/roadmap/cv6-intelligence-runtime-maturity/index.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/index.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/cv6-e5-s1-extension-boundary-and-capability-model/plan.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e3-multi-user-cleanup-and-boundary-audit/cv6-e3-s1-audit-boundary-leaks/plan.md`
- `README.md`
- `REFERENCE.md`

Check specifically that the wording does **not** imply:
- every specialized capability should be moved into core if it is useful
- all “extensions” must be dynamically loaded plugins
- Pi runtime support files are the same thing as user-specific domain extensions
- `review-copy` is already declared permanent core functionality

---

## Validation Commands

```bash
rg -n "extension model|financial-tools|review-copy|xdigest|runtime integration|custom skills" README.md REFERENCE.md docs .pi .claude
```

Then run:

```bash
git diff --check
```

No runtime verification suite is required because no code behavior changes are in scope.
