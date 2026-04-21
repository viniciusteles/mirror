[< CV6.E5.S2 Plan](plan.md)

# CV6.E5.S2 — Test Guide: Establish the first extension migration/reference path

## Scope

This story started as planning/documentation only. `review-copy` has now moved
through that path into an external reference example.

Verification is about confirming that `review-copy` has a concrete, credible
reference-extension path instead of remaining an undefined special case.

---

## Review Checklist

Confirm the docs clearly define:

1. **Classification**
   - `review-copy` is a reference extension, not core

2. **Short-term path**
   - the historical in-repo staging is documented accurately
   - current docs point to the external example/runtime path

3. **Why it is a good example**
   - orchestrates stable core commands
   - generates external artifacts
   - does not require core schema changes

4. **Future path**
   - later location/install model remains open but bounded
   - later work can move it once the extension authoring model is clearer

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/index.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/cv6-e5-s1-extension-boundary-and-capability-model/plan.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/cv6-e5-s2-review-copy-reference-path/plan.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e3-multi-user-cleanup-and-boundary-audit/cv6-e3-s2-resolve-high-risk-boundary-leaks/plan.md`
- `examples/extensions/review-copy/SKILL.md`
- `examples/extensions/review-copy/skill.yaml`

Check specifically that the wording does **not** imply:
- `review-copy` is already part of the permanent core framework
- `review-copy` must be moved immediately before the extension model is usable
- the extension model requires dynamic plugin loading

---

## Validation Commands

```bash
rg -n "review-copy|reference extension|extension model|custom skills|memory consult" docs/project .pi .claude
```

Then run:

```bash
git diff --check
```

Optional runtime verification:

```bash
python -m memory extensions install review-copy --extensions-root examples/extensions --mirror-home /tmp/mm-home
python -m memory extensions expose-claude --mirror-home /tmp/mm-home --target-root /tmp/mm-project
python -m memory extensions clean-claude --target-root /tmp/mm-project
```
