[< Roadmap](../index.md)

# CV4 — Framework/User Separation

**Status:** Done
**Goal:** Turn Mirror Mind into a reusable framework whose repository contains only generic templates, while real user identity and runtime state live in per-user homes under `~/.mirror/<user>/`.

---

## What This Is

CV0 made the system English-first. CV1–CV3 made it dual-interface and Pi-capable.
But the project still carries one user's live identity model too close to the
repository checkout.

CV4 separates those concerns cleanly:
- the repository ships framework code and generic identity templates only
- each real user gets a mirror home under `~/.mirror/<user>/`
- identity YAMLs live under `~/.mirror/<user>/identity/`
- runtime state lives beside them, centered on `~/.mirror/<user>/memory.db`
- user-owned export artifacts, including transcripts, live outside the repo and use configurable paths
- legacy Portuguese-era data migrates into that user-home structure

This is both a product capability and an architectural cleanup. It makes Mirror
Mind reusable by multiple users without baking private identity into the repo.

---

## Target Layout

```text
~/.mirror/<user>/
  identity/
    self/
    ego/
    user/
    organization/
    personas/
    journeys/
  memory.db
  backups/
  exports/
```

Notes:
- `backups/` is the default only; users may point backups elsewhere (for example Dropbox)
- `exports/` is the default only; users may point exports elsewhere
- transcripts are export artifacts, not source files, and should default under `exports/transcripts/` when enabled
- repository templates live under `templates/identity/`, not under a live `identity/` root

---

## Epics

| Code | Epic | User-visible outcome | Status |
|------|------|----------------------|--------|
| CV4.E1 | User Home Layout | Mirror Mind has a documented canonical per-user home under `~/.mirror/<user>/` |
| CV4.E2 | Template Identity in Repo | The repo ships only generic templates under `templates/identity/` |
| CV4.E3 | External Identity Loading and Seeding | Seed/load reads from the user home instead of repo-owned identity files |
| CV4.E4 | Multi-User Foundation | More than one user home can coexist cleanly on one machine |
| CV4.E5 | Legacy Migration into User Home | Old Portuguese-era data migrates into the new user-home layout |
| CV4.E6 | Transcript Export Configuration | Transcript exports are optional, configurable, and stored outside the repo |

---

## Done Condition

CV4 is done when:
- the repository no longer contains live user identity data
- generic templates exist under `templates/identity/`
- runtime identity loading and seeding operate against `~/.mirror/<user>/identity/`
- the canonical runtime database location is `~/.mirror/<user>/memory.db`
- multiple user homes are a first-class supported layout
- legacy `memoria.db`-era data has a documented and tested migration path into the new structure
- transcript exports are configurable, optional, and stored outside the repository

---

## Sequencing

The likely sequence is:

```text
E1 (User Home Layout)
  ├── E2 (Template Identity in Repo)
  ├── E3 (External Identity Loading and Seeding)
  ├── E4 (Multi-User Foundation)
  └── E6 (Transcript Export Configuration)
          \
           └── E5 (Legacy Migration into User Home)
```

E1 should come first because the migration target, export defaults, and seeding
behavior all depend on the user-home contract. E5 should come after the target
layout is stable enough to migrate into. E6 should define transcript export as
a user-owned configurable artifact rather than a repo-tracked file.

Initial configuration direction for E6:
- `TRANSCRIPT_EXPORT_AUTOMATIC=false`
- `TRANSCRIPT_EXPORT_DIR=~/.mirror/<user>/exports/transcripts`

Manual transcript export remains explicit. Automatic transcript export is opt-in.

---

## Out of Scope

- `uv` adoption or Python packaging changes
- client-server architecture
- intelligence-depth improvements such as shadow activation, extraction tuning,
  or search weighting changes (those now belong to CV6)

---

**See also:** [Roadmap](../index.md) · [Briefing](../../briefing.md) · [Decisions](../../decisions.md)
