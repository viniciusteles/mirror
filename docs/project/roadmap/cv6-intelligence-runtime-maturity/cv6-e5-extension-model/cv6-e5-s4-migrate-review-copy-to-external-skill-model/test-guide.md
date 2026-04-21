[< CV6.E5.S4 Plan](plan.md)

# CV6.E5.S4 — Test Guide: Migrate `review-copy` to the external skill model

## Scope

This story now includes a concrete reference migration path for `review-copy`:
example source tree, user-home installation shape, validation/inspection
commands, and explicit runtime sync commands.

Verification is about confirming that the migration path is now concrete,
repeatable, and consistent with the extension contract.

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

5. **Concrete installation flow**
   - copy into `~/.mirror/<user>/extensions/review-copy/`
   - validate and inspect from the user home
   - sync into explicit runtime target roots for Pi and Claude

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/cv6-e5-s2-review-copy-reference-path/plan.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/cv6-e5-s3-external-skill-registry-and-manifest-contract/plan.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/cv6-e5-s4-migrate-review-copy-to-external-skill-model/plan.md`
- `examples/extensions/review-copy/SKILL.md`
- `examples/extensions/review-copy/skill.yaml`

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
python -m memory extensions validate --extensions-root examples/extensions
python -m memory inspect extension review-copy --extensions-root examples/extensions
python -m memory extensions sync --extensions-root examples/extensions --runtime pi --target-root /tmp/review-copy-pi
python -m memory extensions sync --extensions-root examples/extensions --runtime claude --target-root /tmp/review-copy-claude
python -m memory extensions install review-copy --extensions-root examples/extensions --mirror-home /tmp/mm-home
python -m memory extensions expose-claude --mirror-home /tmp/mm-home --target-root /tmp/mm-project
python -m memory extensions clean-claude --target-root /tmp/mm-project

git diff --check
```

Confirm the expected files exist after sync:

```bash
test -f /tmp/review-copy-pi/ext-review-copy/SKILL.md
test -f /tmp/review-copy-pi/extensions.json
test -f /tmp/review-copy-claude/ext:review-copy/SKILL.md
test -f /tmp/review-copy-claude/extensions.json
```
