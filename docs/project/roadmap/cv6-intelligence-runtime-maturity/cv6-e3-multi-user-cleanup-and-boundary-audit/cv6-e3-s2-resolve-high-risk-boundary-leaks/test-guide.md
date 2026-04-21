[< CV6.E3.S2 Plan](plan.md)

# CV6.E3.S2 — Test Guide: Resolve or reclassify the highest-risk boundary leaks

## Scope

This story is primarily planning/documentation. It may inform later doc updates,
but no full extension migration is in scope yet.

Verification is about confirming that the highest-risk boundary-leak candidates
have a concrete, non-hand-wavy resolution path.

---

## Review Checklist

Confirm the docs clearly define a resolution path for:

1. **Former repo-local `engineer` meta persona**
   - removed from the repo
   - treated as a resolved example of a boundary leak
   - not seed input, not runtime identity

2. **`review-copy`**
   - kept temporarily in-repo
   - explicitly classified as a reference extension example
   - handed off to CV6.E5.S2

3. **Pi runtime support files**
   - explicitly distinguished from user-specific extensions

4. **Documentation direction**
   - new users should not confuse `meta/` or reference extensions with user-owned identity or core runtime truth

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e3-multi-user-cleanup-and-boundary-audit/index.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e3-multi-user-cleanup-and-boundary-audit/cv6-e3-s1-audit-boundary-leaks/plan.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e3-multi-user-cleanup-and-boundary-audit/cv6-e3-s2-resolve-high-risk-boundary-leaks/plan.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/cv6-e5-s1-extension-boundary-and-capability-model/plan.md`

Check specifically that the wording does **not** imply:
- removed personalized repo-local persona artifacts are part of the seed/runtime identity path
- `review-copy` is permanently declared core
- runtime-support extensions and user-specific extensions are interchangeable

---

## Validation Commands

```bash
rg -n "reference extension|repo-local|mirror-logger|review-copy|engineer meta persona" docs/project .pi .claude README.md REFERENCE.md
```

Then run:

```bash
git diff --check
```

No runtime verification suite is required because no code behavior changes are in scope.
