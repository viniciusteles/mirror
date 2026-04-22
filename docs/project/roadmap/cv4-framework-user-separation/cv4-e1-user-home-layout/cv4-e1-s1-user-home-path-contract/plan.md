[< CV4.E1 User Home Layout](../index.md)

# CV4.E1.S1 — Plan: Define the user-home path contract and path precedence rules

## What and Why

Before code changes, we need one explicit contract for where Mirror Mind looks
for user-owned state.

Today the project has multiple path assumptions in motion:
- runtime DB under `~/.mirror/`
- identity seeded from repo-owned `identity/`
- backup/export behavior defined elsewhere and not yet aligned to CV4
- transcript artifacts accidentally landing under `src/`

CV4 replaces that ambiguity with a single per-user home rooted at:

```text
~/.mirror/<user>/
```

This story does not implement the layout. It defines the contract that later
stories will implement against.

The outcome should answer, unambiguously:
- what the canonical user-home root is
- how the active user is selected (`MIRROR_HOME`, `MIRROR_USER`, and future CLI overrides)
- what path resolution precedence applies
- which conflict cases fail hard instead of being guessed away
- which paths are part of the contract vs. configurable defaults
- what compatibility story exists for current installs during migration

---

## Proposed Contract

### Canonical root

The canonical user-home root is:

```text
~/.mirror/<user>/
```

This is the ownership boundary for one user's local Mirror Mind state.

### Canonical in-home paths

These are part of the user-home contract:

```text
identity/                 # user-owned seed YAMLs
memory.db                 # runtime source of truth
backups/                  # default backup location only
exports/                  # default export location only
exports/transcripts/      # default transcript export location only
```

### Repo-owned path

The repository owns only generic templates:

```text
templates/identity/
```

These are bootstrap assets, not live identity.

### Configurable vs. fixed

Fixed contract paths:
- user-home root shape
- `identity/`
- `memory.db`

Configurable defaults:
- `backups/`
- `exports/`
- `exports/transcripts/`

### Path resolution precedence

Path resolution should prefer:

1. explicit CLI override (for example `--mirror-home`, later `--user` where appropriate)
2. explicit `MIRROR_HOME`
3. derived `~/.mirror/<user>/` from `MIRROR_USER`
4. otherwise fail clearly

We should avoid hidden fallback to repo-owned live identity.

### User-selection direction

The active user is selected explicitly, not by guessing from directory contents.

The contract is:
- `MIRROR_HOME` is authoritative when set
- `MIRROR_USER` may be used to derive `~/.mirror/<user>/` when `MIRROR_HOME` is not set
- if both `MIRROR_HOME` and `MIRROR_USER` are set and inconsistent, fail hard
- no silent merge between user homes
- no accidental fallback into repo identity as if it were a user home
- normal runtime commands do not auto-create a missing user home; creation belongs to an explicit bootstrap/init flow

---

## Deliverable

This story should produce documentation updates only:
- CV4.E1 epic page
- this plan
- this test guide
- any follow-up wording needed in roadmap/decisions if the contract sharpens

No runtime code changes yet.

---

## Risks and Design Concerns

### 1. Confusing templates with identity
If repo templates and live identity share the same semantics, CV4 collapses.
The contract must keep them distinct.

### 2. Over-designing multi-user selection too early
We need a firm direction, not a full framework. Keep the contract tight and the
selection mechanism simple.

### 3. Letting defaults become hidden runtime truth
`backups/` and `exports/` are defaults, not the source of truth. `memory.db`
and `identity/` are the real contract.

### 4. Migration target instability
Legacy migration should not start until this contract is stable enough to serve
as the destination.

---

## Follow-on Stories Enabled

Once S1 is accepted, the project can plan and implement:
- CV4.E1.S2 (override policy for backups/exports/transcripts)
- CV4.E2 template relocation into `templates/identity/`
- CV4.E3 external identity loading and seeding
- CV4.E4 active-user selection support
- CV4.E5 legacy migration into the user-home layout
- CV4.E6 transcript export configuration
