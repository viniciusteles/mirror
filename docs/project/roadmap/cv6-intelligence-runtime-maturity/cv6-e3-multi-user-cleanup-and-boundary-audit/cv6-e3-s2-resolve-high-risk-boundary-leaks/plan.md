[< CV6.E3 Multi-User Cleanup and Repo Boundary Audit](../index.md)

# CV6.E3.S2 — Plan: Resolve or reclassify the highest-risk boundary leaks

## What and Why

CV6.E3.S1 established that the biggest current boundary problem is not raw
technical coupling, but ambiguity about what certain repo artifacts mean.

The highest-risk items identified there are:
- the now-removed repo-local `engineer` meta persona
- the now-removed repo-local `review-copy` skill files

This story defines the first concrete resolution path for those items without
forcing premature moves that would outrun the extension-model contract.

---

## Highest-Risk Items and Proposed Resolution

### 1. Former repo-local `engineer` meta persona

#### Current issue
The file was useful in repo collaboration, but it was personal enough that new
contributors could mistake it for a framework persona definition.

#### Resolution
The file has now been removed from the repo.

#### Ongoing rule
Do **not** reintroduce repo-local personalized persona files casually. If a
future operational artifact is truly needed, it should either be clearly
classified outside the framework model or kept outside the repo entirely.

#### Why this is the right move
In this case, removal is clearer than continued classification overhead.

### 2. `review-copy` skills

#### Historical issue
`review-copy` used to live in the same in-repo skill surface as more central
Mirror Mind capabilities, even though it was better understood as a
user-specific extension candidate.

#### Resolution status
This path is now complete:
- the existing repo-local skill files were first reclassified in docs as a
  **reference extension example**
- the extension model was defined around a real example
- the repo-local skill files were then removed
- `review-copy` now lives as an external example under
  `examples/extensions/review-copy/`
- the runtime-visible commands are `ext:review-copy` and `ext-review-copy`

#### Why this became the right move
Reclassification gave the extension model something real to point at; removal
finished the boundary cleanup once the install/runtime path existed.

### 3. Pi runtime integration artifacts

#### Current issue
The word "extension" in `.pi/extensions/mirror-logger.ts` could be confused with
user-specific extensions.

#### Proposed resolution
Document and preserve it as a **core runtime integration artifact** rather than
part of the extension model for domain capabilities.

#### Why this matters
The extension model should not accidentally absorb runtime support files.

---

## Proposed Documentation Outcomes

This story should establish the following explicit wording direction:

### In docs and roadmap language
- removed repo-local `engineer` meta persona = resolved boundary-leak example
- `review-copy` = external reference extension example
- `.pi/extensions/mirror-logger.ts` = core runtime integration artifact
- `financial-tools` / `xdigest` = external extensions/tools

### In onboarding language
New users should learn:
- edit user identity under `~/.mirror/<user>/identity/`
- do not treat `meta/` as user identity
- not every shipped skill is automatically part of Mirror Mind core forever
- specialized workflows may live as extensions or reference extensions

---

## Questions This Story Should Settle

1. What wording should mark an in-repo capability as a reference extension rather than core?
2. Should reference extensions get their own documented location later, or is classification enough for now?
3. Which docs are the minimum necessary to update first so new users do not get the wrong model?
4. Should `review-copy` remain in the default command inventory while reclassified, or should it move to an extension section in docs immediately?

---

## Recommended Direction

- resolve ambiguity first through explicit reclassification
- avoid moving files until the extension reference path is defined
- keep repo-local personalized persona artifacts out of the repo unless they have a compelling, clearly documented reason to exist
- keep `review-copy` out of the repo-local runtime skill surfaces now that the
  external path exists
- preserve Pi runtime support files as core runtime integrations, not extension examples

---

## Deliverable

This story should produce:
- the explicit resolution path for the highest-risk boundary leaks
- a documentation direction for how those items are labeled
- the handoff into CV6.E5.S2 for `review-copy` as the first reference extension

Implementation began as doc updates and reclassification language, and has now
progressed through the full `review-copy` extension migration.

---

## Risks and Design Concerns

### 1. Leaving ambiguity in place too long
If the classification is agreed but not reflected in docs, the system stays confusing.

### 2. Moving too early
If `review-copy` is moved before the extension reference path is documented, the
result may be a cleaner tree but a muddier model.

### 3. Treating “reference extension” as permanent limbo
The reference-extension category is useful only if it leads to a clearer future path.

---

## Follow-on Work Enabled

Once S2 is accepted, later work can:
- update README/REFERENCE/onboarding docs with the new classification
- define the concrete `review-copy` reference path in CV6.E5.S2
- decide whether to introduce a dedicated reference-extension location later
