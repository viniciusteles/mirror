[< CV6.E5 Extension Model for User-Specific Capabilities](../index.md)

# CV6.E5.S4 — Plan: Migrate `review-copy` to the external skill model

## What and Why

CV6.E5.S2 establishes `review-copy` as the first reference extension path. CV6.E5.S3 defines the external skill registry and manifest contract. This story connects them by defining the migration path for the first real capability.

`review-copy` is the ideal first migration target because:
- it is already useful
- it is already cross-runtime
- it is clearly not core
- it already demonstrates the desired extension pattern of orchestrating stable core commands

---

## Proposed Migration Target

Target shape:

```text
~/.mirror/<user>/extensions/review-copy/
  skill.yaml
  SKILL.md
```

Runtime-visible names:
- Claude Code: `ext:review-copy`
- Pi: `ext-review-copy`

The extension remains prompt-driven unless later complexity justifies a command-backed runner.

---

## Migration Phases

### Phase 1 — Parallel reference form

Introduce the external-skill shape for `review-copy` while the in-repo reference remains documented.

Goals:
- prove the manifest/location model can represent a real skill
- avoid breaking existing users immediately
- keep the old and new forms comparable during transition

### Phase 2 — Prefer external form

Once discovery/registration exists:
- prefer the user-home external version
- keep in-repo docs only as a migration aid if still needed

### Phase 3 — Remove or archive in-repo reference

Once the external skill path is stable and documented:
- remove the in-repo `review-copy` skill files from the default core surface
- keep historical roadmap/docs accurate

---

## Contract `review-copy` Must Follow

The migrated external skill should:
- declare itself through `skill.yaml`
- expose a prompt-skill entrypoint via `SKILL.md`
- call stable core commands such as `python -m memory consult`
- avoid direct reliance on Mirror internal module imports
- generate external artifacts without changing core schema

---

## Questions This Story Should Settle

1. Should the first migration keep the exact same command text and only add a new namespaced alias, or switch directly to `ext:` / `ext-` names?
2. How long should the in-repo reference remain after the external path exists?
3. What user migration guidance is needed so existing workflows do not become confusing?
4. Does `review-copy` stay prompt-driven, or is there any benefit to a command-backed runner later?

---

## Recommended Direction

- migrate `review-copy` first as a **prompt-skill external extension**
- use the new manifest + user-home extension directory model
- adopt `ext:review-copy` / `ext-review-copy` as the explicit external command surface
- keep the in-repo version only long enough to support transition and documentation

---

## Deliverable

This story should produce:
- the first concrete migration design for a real extension skill
- naming, location, and compatibility decisions for `review-copy`
- input into the eventual implementation of external skill discovery

Implementation belongs to later work.

---

## Risks and Design Concerns

### 1. Two parallel versions for too long

If both in-repo and external versions linger without a preference rule, users will get confused.

### 2. Premature migration before discovery exists

The external target should not outrun the registry/discovery contract.

### 3. Losing the example value

If `review-copy` moves too abruptly, it may become harder to use as the teaching example for the extension model.

---

## Follow-on Work Enabled

Once S4 is accepted, later work can:
- implement the first external skill discovery flow
- publish migration guidance for `review-copy`
- test the first real non-core skill living outside the Mirror repo
