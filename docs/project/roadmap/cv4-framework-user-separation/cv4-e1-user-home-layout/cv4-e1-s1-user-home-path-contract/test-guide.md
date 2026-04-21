[< CV4.E1.S1 Plan](plan.md)

# CV4.E1.S1 — Test Guide: Define the user-home path contract and path precedence rules

## Scope

This story is planning/documentation only. There is no runtime implementation in
scope yet.

The purpose of verification is to confirm that the documented contract is:
- internally consistent
- aligned with CV4
- aligned with Briefing D3 and Decisions
- precise enough for later implementation stories

---

## Review Checklist

Confirm the docs state all of the following clearly:

1. **Canonical user-home root**
   - `~/.mirror/<user>/`

2. **Canonical fixed paths**
   - `identity/`
   - `memory.db`

3. **Default but configurable paths**
   - `backups/`
   - `exports/`
   - `exports/transcripts/`

4. **Repo-owned bootstrap assets**
   - `templates/identity/`
   - templates are not live user identity

5. **Precedence principle**
   - explicit CLI override > `MIRROR_HOME` > derived `~/.mirror/<user>` from `MIRROR_USER` > clear failure

6. **Selection principle**
   - active user selection is explicit
   - `MIRROR_HOME` is authoritative when set
   - conflicting `MIRROR_HOME` and `MIRROR_USER` values fail hard
   - no silent merge between user homes
   - no fallback to repo identity as live identity
   - normal runtime commands do not auto-create a missing user home

7. **Out-of-scope clarity**
   - no code changes yet
   - no `uv` work
   - no migration implementation yet

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/briefing.md`
- `docs/project/decisions.md`
- `docs/project/roadmap/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e1-user-home-layout/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e1-user-home-layout/cv4-e1-s1-user-home-path-contract/plan.md`

Specifically check for any stale references to:
- `~/.config/mirror/`
- repo-owned live identity as the seed source
- transcript artifacts under `src/`

---

## Validation Commands

```bash
rg -n "~/.config/mirror|templates/identity|~/.mirror/<user>|exports/transcripts|repo-owned live identity|transcript" docs/project docs/process docs/index.md
```

Then run the standard doc hygiene checks:

```bash
git diff --check
```

No code verification suite is required for this story because no runtime behavior
changes are in scope.
