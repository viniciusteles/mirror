[< CV4.E4 Multi-User Foundation](../index.md)

# CV4.E4.S1 — Plan: Define the active-user selection model and conflict rules

## What and Why

CV4.E1 already established the path-resolution direction:
- CLI override first
- `MIRROR_HOME` next
- derived `~/.mirror/<user>/` from `MIRROR_USER` next
- otherwise fail clearly

This story takes that contract and frames it explicitly as a multi-user model.

Without this story, multi-user support would remain an accidental side effect of
path variables rather than a documented design. That is risky. Features like
seeding, backup, transcript export, and migration all need to know which user
home they are operating on, and they must never guess incorrectly.

---

## Proposed Multi-User Model

### User homes

Each user has an isolated home under:

```text
~/.mirror/<user>/
```

Examples:

```text
~/.mirror/vinicius/
~/.mirror/pati/
~/.mirror/example-user/
```

The presence of multiple directories does not imply automatic selection logic.
Selection must remain explicit.

### Active-user selection precedence

The active user home is resolved by:

1. explicit CLI override (later, e.g. `--mirror-home`, then `--user` where appropriate)
2. `MIRROR_HOME`
3. derived `~/.mirror/<user>/` from `MIRROR_USER`
4. otherwise fail clearly

### Conflict rules

- if `MIRROR_HOME` and `MIRROR_USER` are both set and inconsistent, fail hard
- if no explicit selection can be resolved, fail hard
- if the resolved user home does not exist, normal runtime commands fail clearly
- no scanning of `~/.mirror/` to pick "the only user" or "the newest user"
- no silent merge or fallback between user homes

---

## Recommended Direction

- explicit selection over convenience
- deterministic failure over clever guessing
- one command invocation targets one user home
- user homes are isolated operational units

This is enough to support multi-user usage without introducing a full user/account subsystem.

---

## Questions This Story Should Settle

1. Should any command be allowed to enumerate existing user homes, or is that out of scope for CV4?
2. When both `MIRROR_HOME` and `MIRROR_USER` are absent, should the error message suggest bootstrap/init steps explicitly?
3. Which commands will need CLI overrides earliest (seed, backup, export, migration)?
4. Should docs standardize one preferred configuration style (`MIRROR_HOME` only vs both variables shown)?
5. How should examples refer to multiple users without implying a built-in account model?

---

## Deliverable

This story should produce planning/docs that define:
- the explicit active-user selection model
- the multi-user conflict rules
- the fail-hard behavior that prevents ambiguous user targeting

Implementation belongs to later stories.

---

## Risks and Design Concerns

### 1. Accidental single-user fallback
If code starts assuming there is only one user home, CV4's multi-user claim becomes false.

### 2. Convenience-driven guessing
Auto-picking a user home would create hidden, fragile behavior and make debugging hard.

### 3. Config inconsistency
If docs show too many competing patterns, users will not know which configuration is canonical.

### 4. Account-model creep
We want isolated local user homes, not a whole authentication/account framework.

---

## Follow-on Work Enabled

Once S1 is accepted, later stories can plan:
- multi-user-safe behavior for seed/export/migration commands
- user-home discovery tooling if explicitly desired
- clearer user-scoped error messages and CLI flags
