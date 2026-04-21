[< CV4.E5 Legacy Migration into User Home](../index.md)

# CV4.E5.S1 — Plan: Define the migration source/target contract and safety rules

## What and Why

The original idea behind this track was to create a script that migrates an old
Portuguese-era database (`memoria.db`) into the new English architecture.

That is correct, but incomplete. Before implementation we need to define the
migration contract explicitly:
- what counts as a valid legacy source
- what the migration target is
- how source and destination are selected
- what safety checks exist
- what the operation is allowed to do automatically vs. only explicitly

This story defines that contract so the future migration tool is deliberate,
user-scoped, and safe.

---

## Proposed Migration Contract

### Legacy source

The primary legacy source is an older Mirror Mind database such as:

```text
memoria.db
```

Potentially accompanied by older surrounding layout assumptions.

The migration contract should treat the source as explicit input, not as
something discovered silently.

### Destination

The migration destination is one explicit user home under:

```text
~/.mirror/<user>/
```

with the runtime database target at:

```text
~/.mirror/<user>/memory.db
```

### User scoping

Migration is a user-scoped operation.
One migration run targets one explicit destination user home.
It must not:
- migrate into multiple homes at once
- guess destination from unrelated directories
- spread imported state across homes implicitly

---

## Safety Rules

### 1. Explicit source and explicit destination

Migration should require clear source and destination resolution. This is not a
background upgrade.

### 2. No in-place mutation of the legacy source

The migration should not rewrite the original legacy database in place.
The source should remain intact.

### 3. Safety before convenience

The migration flow should support inspection/rehearsal/validation rather than a
single opaque import step.

### 4. No silent merge into an existing target without defined rules

If the destination user home or `memory.db` already contains data, the migration
must not silently blend legacy data into it without explicit policy.

### 5. Clear reporting

A migration run should be able to explain:
- what source was used
- what destination was targeted
- what was migrated
- what was skipped or failed

---

## Recommended Direction

- explicit source path
- explicit destination user home
- non-destructive source handling
- user-scoped migration only
- validation/reporting as part of the normal migration path
- no hidden upgrade behavior folded into normal runtime startup

---

## Questions This Story Should Settle

1. Should destination selection prefer `MIRROR_HOME` or require an explicit migration target every time?
2. Should migration into a non-empty target DB be forbidden, allowed with confirmation, or handled by explicit mode selection?
3. What pre-flight validation is required before translation begins?
4. Should migration produce a report artifact by default?
5. Which parts of legacy surrounding state, beyond the DB itself, are in scope for later migration stories?

---

## Deliverable

This story should produce planning/docs that define:
- the migration source/target contract
- the safety posture for migration operations
- the explicitness requirements for source, destination, and reporting

Implementation belongs to later stories.

---

## Risks and Design Concerns

### 1. Accidental destructive behavior
Any migration that mutates the source or silently merges into destination is too risky.

### 2. Overloading runtime startup
Migration should be an explicit operation, not hidden inside normal program startup.

### 3. Ambiguous destination targeting
In a multi-user architecture, migration must never guess the target user home.

### 4. Translating before defining the target
Schema translation work is wasted if the destination contract is still muddy.

---

## Follow-on Work Enabled

Once S1 is accepted, later stories can plan:
- schema/vocabulary translation rules
- dry-run/rehearsal/reporting behavior
- non-empty destination handling
- tests and fixtures for legacy-to-user-home migration
