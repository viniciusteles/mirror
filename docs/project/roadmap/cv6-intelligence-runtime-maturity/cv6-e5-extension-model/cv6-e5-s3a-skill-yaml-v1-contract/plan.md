[< CV6.E5 Extension Model for User-Specific Capabilities](../index.md)

# CV6.E5.S3A — Plan: Define the `skill.yaml` v1 contract

## What and Why

CV6.E5.S3 defines the external skill registry and manifest model. The next step
is to remove ambiguity from the manifest itself.

Without an explicit `skill.yaml` contract, later implementation work would still
have to guess:
- which fields are required
- which fields depend on skill kind
- what runtimes may assume
- how names and entrypoints should be validated

This story defines the first version of that contract.

---

## Scope

This story defines the **v1 manifest schema direction** for external skills.
It does not implement parsing or discovery yet.

The contract should be small, explicit, and sufficient for the first two skill
kinds already planned:
- prompt-skill extension
- command-backed extension

---

## Proposed `skill.yaml` v1 Shape

### Example — prompt-skill extension

```yaml
id: review-copy
name: Review Copy
category: extension
kind: prompt-skill
summary: Multi-LLM copy review workflow
version: 1.0.0

runtimes:
  claude:
    command_name: ext:review-copy
    skill_file: SKILL.md
  pi:
    command_name: ext-review-copy
    skill_file: SKILL.md
```

### Example — command-backed extension

```yaml
id: xdigest
name: X Digest
category: extension
kind: command-skill
summary: Generate digest reports from X/Twitter sources
version: 1.0.0

entrypoint:
  command: python run.py

runtimes:
  claude:
    command_name: ext:xdigest
  pi:
    command_name: ext-xdigest
```

---

## Required Fields

### Common required fields

All external skills should require:
- `id`
- `name`
- `category`
- `kind`
- `summary`
- `runtimes`

### Required field meanings

#### `id`
- stable machine-readable skill id
- lowercase kebab-case
- unique within the resolved extension registry

Examples:
- `review-copy`
- `xdigest`
- `finance-report`

#### `name`
- human-readable display name
- free text

#### `category`
- for v1, fixed value: `extension`
- kept explicit so the file is self-describing and future evolution remains possible

#### `kind`
Allowed v1 values:
- `prompt-skill`
- `command-skill`

#### `summary`
- one-line human-readable description
- short enough for listings and help surfaces

#### `runtimes`
- map of runtime-specific exposure information
- initial runtime keys in scope:
  - `claude`
  - `pi`

At least one runtime must be declared.

---

## Conditional Fields

### For `prompt-skill`

Each declared runtime must provide:
- `command_name`
- `skill_file`

#### `command_name`
- runtime-visible invocation name
- should follow the external namespace convention:
  - Claude: `ext:<id>`
  - Pi: `ext-<id>`

#### `skill_file`
- relative path from the extension root
- expected to point to a markdown skill file, typically `SKILL.md`

### For `command-skill`

The manifest must provide:
- `entrypoint.command`

Each declared runtime must provide:
- `command_name`

#### `entrypoint.command`
- command string executed from the extension root
- examples:
  - `python run.py`
  - `./run.sh`

V1 should treat this as an explicit external command contract, not as code loaded into Mirror.

---

## Optional Fields

Reasonable v1 optional fields:
- `version`
- `description`
- `tags`

### `version`
- semantic version string if provided
- useful for debugging and compatibility later

### `description`
- longer free-text description
- optional because `summary` should cover first-listing needs

### `tags`
- list of short labels for future listing/filtering
- optional and non-authoritative in v1

---

## Runtime Assumptions

Mirror may assume:
- `id` is stable and unique
- the extension root contains `skill.yaml`
- all relative paths are resolved from the extension root
- unknown runtimes are ignored unless later explicitly supported

Mirror should not assume:
- more than the declared runtime metadata
- that command-skills expose prompt markdown
- that prompt-skills have executable entrypoints
- that external skills may import Mirror private internals safely

---

## Validation Rules

Recommended v1 validation rules:
- fail if `id` is missing or not kebab-case
- fail if `kind` is not one of the v1 supported values
- fail if no runtimes are declared
- fail if a declared runtime lacks `command_name`
- for `prompt-skill`, fail if a runtime lacks `skill_file`
- for `command-skill`, fail if `entrypoint.command` is missing
- fail if referenced files do not exist when validation tooling is added later

---

## Questions This Story Should Settle

1. Should `category` remain explicit in v1 or be implied by location?
2. Should `version` be optional or required in v1?
3. Is `command-skill` the right term, or should it be `command-backed` in the manifest too?
4. Should runtime names be limited to `claude` and `pi` in v1, or left open with validation warnings?
5. Should `description` and `tags` be part of v1 or postponed entirely?

---

## Recommended Direction

- keep the manifest minimal and explicit
- require only what discovery and invocation truly need
- support exactly two kinds in v1: `prompt-skill` and `command-skill`
- make runtime entrypoints explicit rather than inferred magically
- use strict validation rules early to keep the extension surface trustworthy

---

## Deliverable

This story should produce planning/docs that define:
- the required and optional `skill.yaml` v1 fields
- the conditional requirements per skill kind
- naming and validation rules
- examples for `review-copy` and `xdigest`

Implementation belongs to later discovery work.

---

## Risks and Design Concerns

### 1. Schema bloat too early

If too many optional fields land in v1, discovery becomes heavier before it is useful.

### 2. Hidden inference rules

If the runtime has to guess too much from missing fields, the manifest loses value.

### 3. Naming drift

If command naming conventions are not explicit, the core/external boundary will blur again.

---

## Follow-on Work Enabled

Once S3A is accepted, later work can:
- implement manifest validation
- implement extension discovery against real `skill.yaml` files
- create the first sample external skill tree for `review-copy`
- add extension authoring guidance with a concrete manifest example
