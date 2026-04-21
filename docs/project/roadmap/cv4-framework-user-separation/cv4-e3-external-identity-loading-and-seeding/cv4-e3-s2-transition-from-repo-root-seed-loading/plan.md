[< CV4.E3 External Identity Loading and Seeding](../index.md)

# CV4.E3.S2 — Plan: Transition from repo-root seed loading to user-home seed loading

## What and Why

CV4.E3.S1 defines the contract: seeding must read from the active user home,
not from repo-owned identity files. This story plans the implementation
transition from the current model to that target.

Today `src/memory/cli/seed.py` is tightly coupled to the repository:
- it finds repo root via `CLAUDE.md`
- it reads fixed paths under `identity/`
- it assumes repo structure is the runtime seed input

That coupling must be removed carefully. A direct switch without planning could:
- break current workflows abruptly
- leave docs and CLI behavior inconsistent
- blur temporary compatibility behavior into permanent architecture

This story defines how to move the seed path resolution safely and explicitly.

---

## Current Coupling To Replace

Current `seed.py` behavior includes:
- `find_repo_root()` using `CLAUDE.md`
- `IDENTITY_MAP` pointing to `identity/self/...`, `identity/ego/...`, etc.
- persona loading from `repo_root / "identity" / "personas"`
- journey loading from `repo_root / "identity" / "journeys"`

That is exactly the repo-root assumption CV4 must retire.

---

## Proposed Transition Strategy

### 1. Introduce user-home identity resolution first

Before removing repo-root assumptions, seed loading should gain one explicit
way to resolve the user-home identity root via the CV4.E1 contract:
- explicit override later
- `MIRROR_HOME`
- derived home from `MIRROR_USER`

### 2. Keep compatibility narrow and time-bounded

If transitional compatibility is needed, it should be explicit and temporary.
The system should not silently choose repo identity when user-home identity is
missing.

Any compatibility behavior should be clearly one of:
- a documented temporary fallback behind an explicit mode/flag
- or a separate migration/bootstrap operation

### 3. Update docs and runtime wording together

The code change cannot happen in isolation. Once user-home seed loading becomes
the intended model, docs like `docs/getting-started.md` must stop telling users
to edit repo `identity/` as the normal workflow.

### 4. Remove repo-root discovery from the steady-state model

Long term, seed loading should not need `find_repo_root()` to locate live
identity. Repo-root discovery may still be useful for template/bootstrap logic,
but not for runtime seeding.

---

## Recommended Direction

- make user-home identity resolution the new default seed path
- treat repo-root seed loading as transitional only
- prefer explicit compatibility controls over hidden fallback behavior
- update docs in the same implementation cycle that changes seed behavior
- remove repo-root identity discovery from steady-state seeding once the replacement path is working

---

## Questions This Story Should Settle

1. Should transitional compatibility exist in `seed.py` itself, or as a separate bootstrap/migration path?
2. If compatibility exists temporarily, how is it activated explicitly?
3. In what order should docs, config, and CLI behavior change to avoid user confusion?
4. Which tests need to shift from repo-root fixtures to user-home fixtures?
5. When is it safe to delete repo-root seed assumptions entirely?

---

## Deliverable

This story should produce planning/docs that define:
- the transition path from repo-root seed loading to user-home seed loading
- the acceptable scope of temporary compatibility behavior
- the documentation synchronization needed during implementation

Implementation belongs to later stories.

---

## Risks and Design Concerns

### 1. Hidden fallback becoming permanent
If repo-root fallback is added casually, it may survive long after CV4 and keep the architecture muddy.

### 2. Docs/runtime mismatch
If seed behavior changes but docs still instruct repo editing, the user experience will become contradictory.

### 3. Test suite lag
Current tests may encode repo-root assumptions. Those need deliberate migration, not incidental breakage.

### 4. Bootstrap vs seed confusion
If the transition uses repo templates as if they were runtime identity, the separation CV4 is trying to establish will collapse.

---

## Follow-on Work Enabled

Once S2 is accepted, later stories can plan:
- concrete `src/memory/cli/seed.py` refactoring
- config/path-resolution updates in `src/memory/config.py`
- test fixture migration from repo-root identity to user-home identity
- getting-started and operational docs updates for the new seed model
