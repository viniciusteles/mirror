[< CV6.E5.S3A Plan](plan.md)

# CV6.E5.S3A — Test Guide: Define the `skill.yaml` v1 contract

## Scope

This story is planning/documentation only. No manifest parser or discovery code
is in scope yet.

Verification is about confirming that the docs define a concrete, implementable
v1 manifest contract for external skills.

---

## Review Checklist

Confirm the docs clearly define:

1. **Required common fields**
   - `id`, `name`, `category`, `kind`, `summary`, `runtimes`

2. **Supported v1 kinds**
   - `prompt-skill`
   - `command-skill`

3. **Conditional requirements**
   - `skill_file` for prompt-skills
   - `entrypoint.command` for command-skills
   - `command_name` for declared runtimes

4. **Naming and validation rules**
   - kebab-case `id`
   - runtime naming guidance
   - failure cases are explicit

5. **Worked examples**
   - `review-copy`
   - `xdigest`

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/cv6-e5-s3-external-skill-registry-and-manifest-contract/plan.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/cv6-e5-s3a-skill-yaml-v1-contract/plan.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/cv6-e5-extension-model/cv6-e5-s4-migrate-review-copy-to-external-skill-model/plan.md`

Check specifically that the wording does **not** imply:
- skill manifests can stay vague and still be supported
- runtimes should infer entrypoints silently from missing fields
- external skills share the same undifferentiated naming surface as core skills

---

## Validation Commands

```bash
rg -n "skill.yaml|prompt-skill|command-skill|entrypoint.command|command_name" docs/project
```

Then run:

```bash
git diff --check
```

No runtime verification suite is required because no code behavior changes are in scope.
