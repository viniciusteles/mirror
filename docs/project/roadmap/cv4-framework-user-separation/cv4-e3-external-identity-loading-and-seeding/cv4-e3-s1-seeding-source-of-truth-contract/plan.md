[< CV4.E3 External Identity Loading and Seeding](../index.md)

# CV4.E3.S1 — Plan: Define the seeding source-of-truth contract for user-home identity

## What and Why

CV4 changes a foundational assumption: the repository is no longer the place
where real identity lives. That means seeding must stop treating repo paths as
the source of truth.

Today `src/memory/cli/seed.py`:
- finds the repository root via `CLAUDE.md`
- reads YAML from `identity/self/`, `identity/personas/`, and `identity/journeys/`
- seeds the database from those repo-owned files

That model conflicts directly with CV4.

This story defines the new contract:
- what seeding reads from
- what templates are for
- how path resolution works at the contract level
- what transitional compatibility is allowed while implementation catches up

---

## Proposed Contract

### Source of truth for seeding

The source of truth for seeding is the active user home:

```text
~/.mirror/<user>/identity/
```

Not:
- `identity/` in the repo
- `templates/identity/` in the repo

### Role of repository templates

`templates/identity/` exists only to bootstrap a new user home. It is not a
runtime seed source.

### Path resolution direction

Seeding follows the same user-home resolution contract established in CV4.E1:

1. explicit CLI override (later)
2. `MIRROR_HOME`
3. derived `~/.mirror/<user>/` from `MIRROR_USER`
4. otherwise fail clearly

### Missing identity behavior

If the resolved user home exists but `identity/` is missing or incomplete,
seeding should apply explicit required/optional rules. It should not silently
fall back to repo identity or templates.

Required core identity:
- `self/`
- `ego/`
- `user/`

Optional identity sections:
- `organization/`
- `personas/`
- `journeys/`

A seed should fail clearly if required core identity is missing. It may succeed
when optional sections are absent.

Bootstrap is a separate flow.

---

## Contract Boundaries

### Seeding owns
- reading user-owned identity YAMLs from the active user home
- validating expected structure exists
- writing those identity layers into the database

### Bootstrap owns
- copying templates from `templates/identity/` into a new user home
- creating initial directory structure for a new user

### Repo does not own
- live user identity at runtime
- silent fallback seed behavior from repo files

---

## Questions This Story Should Settle

1. Should seeding support an explicit path override before broader CLI override work lands?
2. What is the minimum valid user-home identity structure for a successful seed?
3. How should current docs be updated so `/mm-seed` no longer implies repo-owned identity editing?
4. Which compatibility behaviors are acceptable temporarily during CV4 implementation?

---

## Recommended Direction

- seed from the user home only
- fail clearly when required core identity is missing or invalid
- allow absent optional sections without pretending they exist
- keep bootstrap and seeding as separate concepts
- do not let `templates/identity/` become a hidden runtime fallback
- keep any temporary compatibility behavior explicit, narrow, and time-bounded

---

## Deliverable

This story should produce planning/docs that define:
- the seeding source-of-truth contract
- the separation between bootstrap templates and runtime identity
- the failure behavior for missing user-home identity

Implementation belongs to later stories.

---

## Risks and Design Concerns

### 1. Hidden template fallback
If the system quietly seeds from templates, a user may think they are seeding
real identity when they are not.

### 2. Half-migrated path assumptions
If seeding moves but docs still instruct users to edit repo `identity/`, the
system becomes confusing.

### 3. Overly rigid first cut
We need clear failure behavior without forcing every future CLI override detail
into this story.

### 4. Bootstrap/seed conflation
Bootstrap creates a user-home identity tree. Seeding loads it into the DB. They
are related, but not the same operation.

---

## Follow-on Work Enabled

Once S1 is accepted, later stories can plan:
- seed implementation changes in `src/memory/cli/seed.py`
- config/path-resolution changes needed to support the contract
- docs updates for user-home identity editing and seeding
- compatibility removal from repo-root seed assumptions
