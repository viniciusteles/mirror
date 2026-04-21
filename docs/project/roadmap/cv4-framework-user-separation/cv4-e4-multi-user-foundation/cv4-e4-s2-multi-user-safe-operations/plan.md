[< CV4.E4 Multi-User Foundation](../index.md)

# CV4.E4.S2 — Plan: Define multi-user-safe behavior for user-scoped operations

## What and Why

CV4.E4.S1 defines how the active user is selected. This story defines what that
means operationally for commands and workflows that act on user-owned state.

In a multi-user model, commands must not merely know that user homes exist.
They must behave safely and predictably when operating on one of them.

This matters especially for:
- seeding
- backups
- transcript export
- migration/import
- any future command that reads or writes user-owned identity or artifacts

The core principle is simple:

> one invocation targets one user home, explicitly and deterministically.

No command should ever spread work across multiple user homes implicitly.

---

## Proposed Multi-User-Safe Rules

### 1. One operation targets one resolved user home

Each user-scoped operation resolves exactly one active user home via the CV4.E1 /
CV4.E4.S1 selection contract. It must not:
- operate on all homes by default
- merge data between homes
- infer a different home halfway through execution

### 2. User-scoped outputs stay scoped

Artifacts created by an operation belong to the resolved user home unless an
explicit override redirects them elsewhere.

Examples:
- seeding reads from one user's `identity/`
- default backups originate from one user's `memory.db`
- transcript export writes for one user's sessions/artifacts
- migration/import targets one destination home

### 3. Cross-user actions require explicit orchestration

If a future workflow ever needs to process multiple user homes, that must be an
explicit orchestrator-level operation, not a side effect of normal user-scoped
commands.

### 4. Error messages should stay user-scoped

When a command fails, the message should make it clear which user home was being
used or attempted. This is especially important in multi-user environments.

---

## Recommended Direction By Operation Type

### Seed
- reads from exactly one user home's `identity/`
- writes to that user's database/runtime target only
- fails clearly if the user home is unresolved or invalid

### Backup
- backs up the active user's database only
- default destination derives from that user's home unless overridden
- no implicit shared backup aggregation across users

### Transcript export
- exports transcripts for the active user's conversations/artifacts only
- default destination derives from that user's export root unless overridden
- no implicit writing into another user's export space

### Migration/import
- reads one explicit source
- writes into one explicit destination user home
- never guesses destination from the existence of other homes

---

## Questions This Story Should Settle

1. Which existing commands are user-scoped from CV4 onward vs. remain framework-scoped?
2. Should command help/error output include the resolved user home when relevant?
3. Which commands need explicit user/home override flags earliest?
4. Should any command support bulk multi-user operation in CV4, or should that be fully deferred?
5. How should tests encode multi-user isolation expectations clearly?

---

## Recommended Direction

- treat user-scoped operations as single-home operations by default
- make output and failure messages user-scoped and explicit
- defer bulk/multi-home orchestration unless there is a concrete need
- prefer clear isolation over convenience shortcuts

---

## Deliverable

This story should produce planning/docs that define:
- the rules for multi-user-safe command behavior
- the single-home targeting principle for user-scoped operations
- the expectations for explicitness in outputs and failures

Implementation belongs to later stories.

---

## Risks and Design Concerns

### 1. Implicit cross-user behavior
Even one command that accidentally spills across homes would undermine the whole model.

### 2. Hidden destination confusion
A backup or export command that does not make the active home clear becomes hard to trust.

### 3. Early bulk-operation scope creep
Trying to design bulk multi-user workflows too early would distract from the core architecture.

### 4. Inconsistent scoping across commands
If seed is user-scoped but backup/export/migration are not, the model becomes incoherent.

---

## Follow-on Work Enabled

Once S2 is accepted, later stories can plan:
- user-scoped CLI behavior and flags for seed/backup/export/migration
- clearer user-home-aware error messages
- multi-user isolation tests for command behavior
