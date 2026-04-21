[< CV6.E5 Extension Model for User-Specific Capabilities](../index.md)

# CV6.E5.S2 — Plan: Establish the first extension migration/reference path

## What and Why

CV6.E5.S1 defines the extension boundary model. This story gives that model a
real reference path using the strongest current candidate: `review-copy`.

`review-copy` is valuable, cross-runtime, and already implemented as a skill in
both Claude Code and Pi. But it is not central to Mirror Mind's identity,
memory, or runtime control-plane model. That makes it ideal as the first
reference extension example.

The point of this story is not to force an immediate extraction into another
repository. The point is to define a concrete path that new users can understand
and that future implementation can follow.

---

## Proposed Positioning of `review-copy`

### Classification
`review-copy` should be treated as a **reference extension**.

Meaning:
- not framework core
- not user-owned identity
- not a runtime integration artifact
- temporarily still shipped in-repo while the extension model matures

### Why keep it in-repo temporarily?
- it is already functional in both runtimes
- it is a strong example for explaining the extension model
- moving it immediately without a broader authoring/install contract would create churn first and clarity later

### Why not keep calling it core?
- it solves a specialized workflow, not a central Mirror Mind capability
- not every user needs it
- it is exactly the kind of capability the extension model is meant to handle

---

## Proposed Reference Path

### Phase 1 — Reclassify, do not move yet

Historical short-term direction:
- keep `.claude/skills/mm:review-copy/SKILL.md`
- keep `.pi/skills/mm-review-copy/SKILL.md`
- document them as a **reference extension example**
- make docs explicit that they are not a required part of core

Status now:
- both repo-local `review-copy` skill files have been removed
- the reference example lives at `examples/extensions/review-copy/`
- runtime-visible names are `ext:review-copy` and `ext-review-copy`

### Phase 2 — Define extension authoring/install expectations

Before moving `review-copy`, define:
- where reference extensions should live long-term
- how they are installed or copied into a user's environment
- what contract they use to call core capabilities like `memory consult`
- what docs new users should read to create their own extension skills

### Phase 3 — Decide final location model

Plausible eventual directions:
1. separate extension repositories
2. user-home extension directories
3. a dedicated in-repo `extensions/` or `examples/extensions/` area for reference examples only

This story should not force the final storage model yet, but it should narrow
which models are acceptable.

---

## Recommended Direction

The recommended reference path is:

- **completed:** `review-copy` was reclassified as a reference extension
- **completed:** the reference example now lives in `examples/extensions/review-copy/`
- **now:** install and surface it explicitly as `ext:review-copy` / `ext-review-copy`
- **later:** keep improving the extension authoring/install/runtime model around this example

This balances clarity and momentum.

---

## Contract `review-copy` Demonstrates

`review-copy` is valuable as a reference example because it demonstrates a good
extension pattern:

- extension-specific workflow logic lives outside the core Python package
- it orchestrates existing core capabilities rather than patching them
- it may call shared commands such as `python -m memory consult`
- it can produce external artifacts (HTML reports) without changing core schema
- it works at the skill/workflow layer rather than the runtime identity layer

That is exactly the kind of extension behavior CV6 wants to encourage.

---

## Questions This Story Should Settle

1. What terminology should docs use for `review-copy`: reference extension, sample extension, or transitional extension?
2. Should reference extensions remain visible in top-level command docs, or move to a separate extension/examples section?
3. What is the minimum install/use story for a user who wants a custom capability like this?
4. Which long-term location model should remain in scope for later implementation?

---

## Deliverable

This story should produce:
- the first concrete migration/reference path for a user-specific capability
- a documented rationale for keeping `review-copy` temporarily in-repo
- the extension behavior contract that `review-copy` exemplifies
- input into future doc and repo-structure changes

Implementation of any relocation belongs to later work.

---

## Risks and Design Concerns

### 1. Permanent transitional state
If `review-copy` is reclassified but never moved or documented properly, the model will stall.

### 2. Abstract extension guidance with no example
Without a real example, the extension model remains theoretical.

### 3. Coupling through convenience
If `review-copy` starts depending on internal implementation details instead of stable commands, it stops being a good example.

---

## Follow-on Work Enabled

Once S2 is accepted, later work can:
- update docs to label `review-copy` explicitly as a reference extension
- decide whether to create a dedicated extension/examples location
- define user guidance for creating similar custom skills
- choose whether `review-copy` should eventually move out of the repo or into a clearer non-core location
