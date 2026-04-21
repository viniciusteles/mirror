[< CV6.E5.S3 Plan](plan.md)

# CV6.E5.S3 — Test Guide: Define the external skill registry and manifest contract

## Scope

This story is planning/documentation only. No runtime implementation of external
skill discovery is in scope yet.

Verification is about confirming that the docs define a concrete, coherent model
for non-core skills that live outside the Mirror repo but remain accessible from
within Mirror.

---

## Review Checklist

Confirm the docs clearly define:

1. **Canonical external skill location**
   - a user-owned extension directory under the Mirror home

2. **Manifest contract**
   - each external skill declares id, kind, runtime support, and entrypoints

3. **Skill kinds**
   - prompt-skill extension
   - command-backed extension

4. **Namespacing**
   - external skills are distinguished from core skills

5. **Boundary rules**
   - no default in-process plugin loading
   - use stable CLI/API/file/artifact interfaces

6. **Reference example mapping**
   - `review-copy` is explained in terms of the new model

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/index.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/cv6-e5-s1-extension-boundary-and-capability-model/plan.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/cv6-e5-s2-review-copy-reference-path/plan.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/cv6-e5-s3-external-skill-registry-and-manifest-contract/plan.md`
- `README.md`
- `REFERENCE.md`

Check specifically that the wording does **not** imply:
- external skills are just undocumented repo-local files
- the model requires dynamic in-process plugin loading
- core and external skills share one undifferentiated namespace
- `review-copy` must remain permanently in-repo

---

## Validation Commands

```bash
rg -n "extensions/|manifest|prompt-skill|command-backed|ext:|ext-" docs/project README.md REFERENCE.md
```

Then run:

```bash
git diff --check
```

No runtime verification suite is required because no code behavior changes are in scope.
