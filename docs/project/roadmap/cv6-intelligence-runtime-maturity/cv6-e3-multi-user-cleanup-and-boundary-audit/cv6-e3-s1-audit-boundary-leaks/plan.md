[< CV6.E3 Multi-User Cleanup and Repo Boundary Audit](../index.md)

# CV6.E3.S1 — Plan: Audit remaining repo/runtime/user-boundary leaks

## What and Why

CV4 removed the old repo-owned live-identity model and moved runtime truth into
user homes plus the database. CV6 has already improved the runtime side further
by making persona routing database-backed. But some artifacts in the repository
still blur the line between:

- framework core
- user-owned identity
- repo-local operational material
- user-specific capabilities that should become extensions

This story is an audit and classification pass. The goal is not to move every
artifact immediately, but to define which remaining items are acceptable as core,
which are transitional, and which should migrate to an extension model.

---

## Audit Scope

This audit should explicitly look at at least these artifacts:

### 1. Former repo-local `engineer` meta persona

Previous role:
- repository-local engineer persona used as an operational collaboration artifact
- clearly not part of the user-home seed flow

Boundary risk:
- it contained Vinícius-specific operational biography and could be mistaken for
  framework-shipped identity

Resolution status:
- the repo-local file has now been removed
- this remains a useful example of the kind of artifact CV6.E3 should identify
  early and either remove or classify explicitly

### 2. `.pi/skills/mm-review-copy/SKILL.md`
### 3. `.claude/skills/mm:review-copy/SKILL.md`

Current role:
- user-specific multi-LLM copy review workflow
- implemented as agent-orchestrated SKILL.md-only behavior in both runtimes

Boundary risk:
- useful capability, but not obviously core to Mirror Mind identity/memory/runtime
- currently shipped as if it were part of the same core skill surface as more
  framework-central commands

Recommended classification:
- **extension candidate** and likely the first reference migration example for CV6.E5

### 4. External financial tooling references

Observed in docs:
- `README.md`
- `REFERENCE.md`

Current role:
- explicit example of a domain-specific external tool living outside the repo

Boundary value:
- this is the healthiest current example of the desired extension boundary
- it should become a positive reference model for CV6.E5

Recommended classification:
- **external extension/tool reference model**, not core

### 5. Pi runtime extension: `.pi/extensions/mirror-logger.ts`

Current role:
- runtime integration glue for Pi session lifecycle and logging

Boundary value:
- despite the name "extension", this one is part of framework runtime support,
  not a user-specific capability
- it should not be confused with the extension model for domain capabilities

Recommended classification:
- **core runtime integration artifact**

---

## Findings So Far

### Finding A — not every repo-local artifact is a bug

Some repo-local artifacts are legitimate if they are clearly classified as:
- development-only
- runtime integration support
- examples or migration material

The problem is not simply “anything user-specific in the repo is forbidden.”
The real problem is ambiguity about ownership and runtime meaning.

### Finding B — `review-copy` is the strongest current extension-model candidate

It is valuable, cross-runtime, and clearly user-specific enough that it should
help define the extension boundary.

### Finding C — repo-local personalized persona artifacts should not linger without a strong reason

The former `engineer` meta persona was not used as seed input or runtime identity
source, but its repo presence still created avoidable ambiguity. Its removal is
consistent with the goal of keeping framework and user-specific operational
material separate.

### Finding D — Mirror Mind already has one implicit extension pattern

The `financial-tools` references show the intended direction:
- domain-specific tooling outside this repository
- Mirror Mind interprets or consumes its output as context

CV6.E5 should formalize that pattern instead of inventing a completely new one.

---

## Questions This Story Should Settle

1. Which current artifacts are genuinely mislocated versus merely undocumented?
2. What explicit classification vocabulary should docs use?
   - core framework feature
   - core runtime integration artifact
   - user-owned identity
   - repo-local development artifact
   - external/user-installed extension
3. Should `review-copy` remain in-repo temporarily as a reference extension, or
   should the first step be to reclassify it before moving it?
4. What documentation needs updating so the boundary is visible to new users?

---

## Recommended Direction

- treat this story as a classification and documentation pass first
- avoid premature file moves before the extension contract is defined
- remove or explicitly classify repo-local personalized artifacts before they become part of the conceptual model
- use `review-copy` as the first concrete extension-model candidate
- use `financial-tools` as the first positive example of the preferred external-tool boundary
- distinguish runtime integration artifacts (for example Pi lifecycle hooks)
  from user-specific extensions

---

## Deliverable

This story should produce:
- an explicit audit of current boundary-leak candidates
- a classification scheme for artifact ownership
- a list of highest-risk items and their proposed resolution path
- input into CV6.E5 extension-model planning

Implementation moves belong to later stories.

---

## Risks and Design Concerns

### 1. Over-correcting by deleting useful repo-local material

Some artifacts are legitimate if they are clearly marked. The goal is clarity,
not indiscriminate removal.

### 2. Defining “extension” too loosely

If every non-core artifact is called an extension without a contract, the result
will still be muddy.

### 3. Repeating CV4 confusion under a new name

If docs fail to distinguish among core, user identity, and extensions, the
system will drift back into the same conceptual blur CV4 tried to remove.

---

## Follow-on Work Enabled

Once S1 is accepted, later stories can:
- update docs to reflect the classification scheme
- move or reclassify the highest-risk items
- define the concrete extension contract in CV6.E5.S1
- choose and execute the first migration/reference path in CV6.E5.S2
