[< CV4.E2 Template Identity in Repo](../index.md)

# CV4.E2.S1 — Plan: Define the template identity structure and content rules

## What and Why

CV4 says the repository should keep only generic identity templates under
`templates/identity/`, while real user identity moves into `~/.mirror/<user>/identity/`.

That sounds simple until we ask what actually counts as a template.

This story defines the rules so later implementation does not drift into one of
two bad outcomes:
- personal identity remains in the repo under a new name
- templates become so empty or abstract that they no longer help bootstrap a user home

The design goal is practical, generic templates:
- structurally complete
- English-first
- personally neutral
- good enough to bootstrap a new user home without carrying one real person's life inside the repo

---

## Proposed Template Structure

Templates should mirror the intended user-home identity layout:

```text
templates/identity/
  self/
  ego/
  user/
  organization/
  personas/
  journeys/
```

This structural mirroring is important because bootstrap should feel like a copy
from template shape into user-home shape, not a translation across unrelated
layouts.

---

## Proposed Content Rules

### Templates should contain
- generic structure
- explanatory comments where useful
- placeholder/example values that teach shape, not biography
- example personas and journeys only if they are clearly generic and non-personal

### Templates should not contain
- Vinícius's live identity
- real personal history, family, business context, or private values
- repo-owned content that the runtime would mistake for a real user profile
- hidden defaults that silently bias bootstrap toward one person's setup

### Language rule
- template files are English-first
- placeholders and comments should teach the intended semantics clearly
- no new Portuguese domain names

---

## Design Questions This Story Should Settle

1. Should templates include example personas/journeys, or only `_template`-style files?
2. How opinionated should placeholder content be?
3. Should template comments live inside YAML files, companion README files, or both?
4. What current repo identity material can be generalized into templates vs. must be removed entirely?
5. How closely should template filenames mirror current seed expectations?

---

## Recommended Direction

- mirror the final user-home identity structure closely
- prefer a small number of strong templates over many half-real examples
- keep template content structurally instructive, not biographical
- use comments/examples to teach shape, but keep runtime semantics clean
- if an example feels personal, it does not belong in the template set

---

## Deliverable

This story should produce planning/docs that define:
- the template directory structure
- the content rules for template files
- the standard for what is generic enough to live in the repo

Implementation belongs to later stories.

---

## Risks and Design Concerns

### 1. Template leakage
A template that still encodes one real user's worldview is not a template.

### 2. Empty-template failure
Templates that are too abstract become useless for onboarding.

### 3. Structural mismatch
If template structure and user-home structure diverge, bootstrap becomes awkward.

### 4. Accidental runtime coupling
The repo template layout must not reintroduce repo-owned live identity as a runtime dependency.

---

## Follow-on Work Enabled

Once S1 is accepted, later stories can plan:
- relocation/creation of template files under `templates/identity/`
- bootstrap/copy flows into `~/.mirror/<user>/identity/`
- cleanup of current repo-owned identity assumptions
