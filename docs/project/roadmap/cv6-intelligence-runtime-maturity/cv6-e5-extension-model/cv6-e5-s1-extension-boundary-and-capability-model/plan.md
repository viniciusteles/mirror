[< CV6.E5 Extension Model for User-Specific Capabilities](../index.md)

# CV6.E5.S1 — Plan: Define the extension boundary and capability model

## What and Why

Mirror Mind now has a cleaner runtime identity model and a better multi-user
story than before, but it still lacks an explicit place for user-specific
capabilities that matter deeply to one user without belonging in framework core.

Three concrete examples motivate this story:

- financial tooling living outside the repo in `~/dev/workspace/financial-tools`
- X digest functionality associated with Henrique's Pi work
- `review-copy`, which currently lives as SKILL.md workflows inside this repo

Without a formal extension model, these capabilities either:
- get absorbed into core by accident
- remain as ad hoc repo-local exceptions
- or move outside the repo without a documented contract

This story defines the contract.

---

## Proposed Capability Boundary Model

### 1. Core framework features

Belong in Mirror Mind core when they are broadly reusable and central to the
product model.

Examples:
- identity loading and runtime composition
- memory storage, search, and extraction
- Mirror Mode and Builder Mode control-plane behavior
- journeys, tasks, conversations, and shared CLI/runtime commands
- runtime integrations required for supported interfaces

### 2. User-owned identity

Belongs in the user's mirror home and database when it expresses who the mirror
is for that user.

Examples:
- self/ego/user/organization identity
- personas and journeys
- user-authored prompt content and persona metadata

### 3. Core runtime integration artifacts

Belong in the repo when they are necessary to support a runtime interface but do
not represent user-specific product capabilities.

Examples:
- `.pi/extensions/mirror-logger.ts`
- skill wrappers that expose core commands consistently across runtimes

### 4. External or user-installed extensions

Belong outside framework core when they are valuable but user-specific,
domain-specific, or organization-specific.

Examples:
- financial import/reporting workflows
- X digest generation
- specialized copy-review pipelines
- custom business or domain automations

---

## Preferred Extension Contract

The preferred extension model is **explicit integration through stable
boundaries**, not arbitrary in-process plugin loading.

Recommended integration styles:
- CLI commands
- API calls
- files or generated artifacts
- imported context or attachments
- user-installed/custom skills orchestrating external tools

Not recommended as the default model:
- importing arbitrary extension code directly into Mirror Mind internals
- patching core services through hidden hooks
- treating extension state as if it were core database schema without an explicit contract

---

## Proposed Classification For Existing Examples

### `financial-tools`

Classification:
- **external extension/tool**

Why:
- separate storage/API concerns
- Mirror Mind interprets its outputs rather than owning its domain tables

### `review-copy`

Classification:
- **extension candidate**

Why:
- useful and cross-runtime
- clearly not central to identity/memory/journeys runtime
- currently in-repo as a skill, but should be treated as a candidate for a more explicit extension path

Recommended first migration/reference path:
- use `review-copy` as the first documented example for CV6.E5.S2

### X digest (`xdigest`)

Classification:
- **external extension/tool**

Why:
- user-specific digest workflow
- better modeled as an external capability than a core mirror concern

---

## First-Cut Extension Rules

A capability should stay out of core if most of these are true:
- it is useful mainly to one user or a narrow subset of users
- it introduces a domain-specific workflow unrelated to identity/memory runtime
- it needs its own storage, importer, or third-party API contract
- it can reasonably communicate with Mirror Mind through text, files, API calls, or attachments
- removing it would not break the basic Mirror Mind product model

A capability can be considered for core when most of these are true:
- it is broadly useful to most users
- it directly supports Mirror Mind's central product model
- both Claude Code and Pi need the capability as part of the standard runtime surface
- it can be documented and tested without relying on one user's private workflow

---

## Questions This Story Should Settle

1. What exact vocabulary should docs use: extension, external tool, user-installed skill, or all three?
2. Should in-repo but non-core examples be allowed temporarily if clearly labeled?
3. Should `review-copy` remain in-repo as a reference extension example before a fuller migration path exists?
4. What minimum contract should an extension satisfy to be considered supported?
5. Where should future extension docs live?

---

## Recommended Direction

- use **extension model** as the umbrella term
- prefer out-of-process integration through CLI/API/files/attachments
- explicitly distinguish runtime integrations from user-specific extensions
- allow transitional in-repo extension examples only when clearly labeled and not confused with core
- treat `review-copy` as the first migration/reference example rather than forcing an immediate move without a contract

---

## Deliverable

This story should produce planning/docs that define:
- the core vs identity vs runtime-integration vs extension boundary model
- the preferred extension integration styles
- the classification of current examples
- the first reference path for follow-on work in CV6.E5.S2

Implementation belongs to later stories.

---

## Risks and Design Concerns

### 1. Turning “extension” into a dumping ground

If the model is too vague, the term will hide design problems instead of solving them.

### 2. Overengineering a plugin platform too early

CV6 needs a clear contract first, not a complex package manager or dynamic loader.

### 3. Confusing runtime integrations with product extensions

Pi lifecycle glue and user-specific domain capabilities are not the same thing.

### 4. Moving too fast without a migration example

The model will stay abstract unless at least one real capability is used to test it.

---

## Follow-on Work Enabled

Once S1 is accepted, later stories can:
- document a supported reference path for `review-copy`
- decide whether in-repo extension examples get a dedicated location or clear labeling
- update onboarding docs so new users know where to add specialized capabilities
- define future extension authoring guidance
