[< CV6.E2.S1 Plan](plan.md)

# CV6.E2.S1 — Test Guide: Define the persona auto-routing contract and scoring rules

## Scope

This story is planning/documentation only. No runtime implementation is in scope.

Verification is about confirming that the docs define a clear, testable,
database-backed routing contract for persona auto-selection.

---

## Review Checklist

Confirm the docs clearly define:

1. **Resolution order**
   - explicit persona
   - session sticky persona
   - global sticky persona
   - detected persona
   - ego fallback

2. **Runtime source of truth**
   - detection reads persona metadata from the database
   - no runtime YAML dependency

3. **Matching behavior**
   - first version is deterministic and keyword-based
   - no-match behavior is explicit
   - ranked candidates are acknowledged

4. **Debuggability**
   - detection should be inspectable/testable, not opaque

---

## Manual Verification

Read these docs together and confirm they agree:

- `CLAUDE.md`
- `docs/project/roadmap/index.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/index.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e1-structured-identity-metadata-in-db/index.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e2-db-backed-persona-auto-routing/index.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e2-db-backed-persona-auto-routing/cv6-e2-s1-persona-auto-routing-contract/plan.md`

Check specifically that the wording does **not** imply:
- auto-routing overrides explicit persona choice
- sticky persona state is ignored casually
- runtime may read repo or user-home persona YAML files directly for routing
- weak matches should always force a persona

---

## Validation Commands

```bash
rg -n "auto-routing|routing contract|sticky persona|ego fallback|database" CLAUDE.md docs/project/roadmap
```

Then run:

```bash
git diff --check
```

No runtime verification suite is required because no code behavior changes are in scope.
