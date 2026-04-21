[< CV6.E5 Extension Model for User-Specific Capabilities](../index.md)

# CV6.E5.S3 — Plan: Define the external skill registry and manifest contract

## What and Why

The extension model is now clear at the architectural level: user-specific
capabilities should not be absorbed into Mirror Mind core by default. But a key
operational question remains unresolved:

How does Mirror expose and invoke a non-core skill that lives outside the Mirror
repo while still making it feel available from within Mirror?

`review-copy` surfaces the problem, but it is not unique. The same question
applies to external financial workflows, X digest generation, and future
user-specific automations.

This story defines the first concrete answer: an **external skill registry and
manifest contract**.

---

## Problem to Solve

Right now Mirror has:
- built-in skill locations inside the repo
- CLI commands inside the core Python package
- no explicit discovery or registration model for skills that live elsewhere

Without a contract, an external skill becomes just “some docs in some folder.”
That is not enough for a stable multi-user framework.

The extension model needs a concrete way to answer:
- where external skills live
- how Mirror discovers them
- how a skill declares what it is
- how a skill exposes runtime entrypoints
- how Mirror distinguishes core skills from external skills

---

## Proposed Model

### 1. Canonical external skill location

Recommended default location:

```text
~/.mirror/<user>/extensions/
```

This keeps the ownership model explicit:
- outside the repo
- inside the user-owned Mirror environment
- not mixed with identity YAMLs
- not confused with framework core

Each extension lives in its own directory, for example:

```text
~/.mirror/<user>/extensions/review-copy/
  skill.yaml
  SKILL.md
```

or

```text
~/.mirror/<user>/extensions/xdigest/
  skill.yaml
  run.py
  README.md
```

### 2. External skill manifest

Each extension should declare itself through a manifest, for example:

```yaml
id: review-copy
name: Review Copy
category: extension
kind: prompt-skill
summary: Multi-LLM copy review workflow
runtimes:
  claude:
    command_name: ext:review-copy
    skill_file: SKILL.md
  pi:
    command_name: ext-review-copy
    skill_file: SKILL.md
```

Or for a command-backed extension:

```yaml
id: xdigest
name: X Digest
category: extension
kind: command-skill
summary: Generate digest reports from X/Twitter sources
entrypoint:
  command: python run.py
runtimes:
  claude:
    command_name: ext:xdigest
  pi:
    command_name: ext-xdigest
```

This manifest should define:
- stable skill id
- human-readable name
- skill kind
- runtime support
- runtime-visible command name
- where the actual skill content or executable entrypoint lives

### 3. Two first-class extension-skill styles

#### A. Prompt-skill extension
Best for model-driven workflows like `review-copy`.

Characteristics:
- workflow lives mainly in `SKILL.md`
- agent orchestrates the process using stable tools and core commands
- no custom code is required by default

#### B. Command-backed extension
Best for workflows with real procedural logic, API calls, or separate runtime concerns.

Characteristics:
- executable entrypoint such as `run.py`, `run.sh`, or another command
- may optionally also ship docs or a skill markdown file
- Mirror invokes a stable external command rather than importing internal code

### 4. Namespacing

Recommended naming convention:
- Claude Code: `ext:review-copy`
- Pi: `ext-review-copy`

Why:
- clearly separates external skills from core `mm:*` / `mm-*` skills
- avoids collision with future core capabilities
- makes the ownership boundary visible to users

---

## Discovery Direction

This story should define the contract first, not the full implementation.

The recommended discovery direction is:
- Mirror loads built-in skills from the repo as it does today
- Mirror also looks in one or more extension directories under the active user home
- manifests are read from those directories
- each manifest contributes one external skill definition to the runtime-visible skill catalog

This is a registry model, not a dynamic in-process plugin model.

---

## Boundary Rules For External Skills

External skills should:
- use documented, stable interfaces
- call core CLI commands when possible
- communicate through CLI, files, APIs, artifacts, or attachments
- keep their own domain-specific state outside Mirror core unless a future explicit API says otherwise

External skills should not, by default:
- import arbitrary Mirror internal modules as an unsupported private API
- patch core services through hidden hooks
- assume repo-relative paths inside the Mirror codebase
- mutate core schema without a documented contract

---

## How `review-copy` Fits This Model

`review-copy` is the best first migration example because it already behaves like
an external prompt-skill in spirit:
- it is workflow-level, not runtime-core
- it orchestrates stable core capabilities such as `python -m memory consult`
- it produces an external HTML artifact
- it does not require core schema changes

Under this model, its likely eventual home would be something like:

```text
~/.mirror/<user>/extensions/review-copy/
  skill.yaml
  SKILL.md
```

with runtime-visible names such as:
- `ext:review-copy`
- `ext-review-copy`

---

## Questions This Story Should Settle

1. Is `~/.mirror/<user>/extensions/` the right canonical first location?
2. What are the minimum required manifest fields for v1?
3. Should the command namespace be `ext:` / `ext-`, or something else?
4. Should prompt-skill and command-skill be the first two supported kinds?
5. What minimal discovery behavior is enough for a first implementation?

---

## Recommended Direction

- adopt an **external skill registry** model rather than ad hoc external files
- use a **manifest-based contract** rather than direct code imports
- support both prompt-skill and command-backed external skills
- place the first canonical external skill root under the active user home
- use explicit `ext:` / `ext-` namespacing to distinguish external skills from core

---

## Deliverable

This story should produce planning/docs that define:
- the external skill directory model
- the manifest schema direction
- the first two supported skill kinds
- naming and discovery conventions
- how `review-copy` maps to that model later

Implementation belongs to later stories.

---

## Risks and Design Concerns

### 1. Reinventing a plugin system too early

The goal is not a large package-management system. The goal is a small, explicit
contract for discovery and invocation.

### 2. Ambiguous ownership

If external skills can live anywhere without a registry, users will not know what is supported.

### 3. Overreliance on private internals

If external skills depend on undocumented internal APIs, the extension model will become brittle.

### 4. Namespace confusion

If external skills use the same command surface as core without distinction, the
ownership boundary will blur again.

---

## Follow-on Work Enabled

Once S3 is accepted, later stories can:
- define the first implementation of extension discovery
- migrate `review-copy` to the external skill model
- document extension authoring for users
- add a real extension catalog/listing view in the future
