[< Project](briefing.md)

# Decisions

Incremental decisions made as the project evolves. Foundational premises live
in [Briefing](briefing.md). This file captures the decisions that came after —
choices made during delivery, lessons learned, and open questions not yet
resolved.

---

## Completed Decisions

### English domain language is complete and tagged

**Date:** 2026-04-17  
**Commits:** `fb0bcf6` through `d425b52`

All runtime paths — Python API, CLI, schema, config, seed, hooks, skills,
identity YAMLs, and docs — use English names. The migration took 9 sessions and
~40 commits. Compatibility aliases and runtime fallbacks have been removed.
Migration-only support remains in database migrations and migration rehearsal
code to allow upgrading old databases.

The full inventory is in `docs/english-domain-language-migration-plan.md`.

---

### Pi adoption ports interface ideas from `mirror-pi`, not the old `memoria` core

**Date:** 2026-04-17  
**Reference:** `docs/process/spikes/pi-runtime-adoption-2026-04-17.md`

The `~/dev/workspace/mirror-pi` spike (Henrique's project) is pre-English-migration
and still uses `memoria`, `travessia`, `.espelho`. It is useful as a working
spike — particularly the `.pi/extensions/mirror-logger.ts` pattern and the Pi
session lifecycle handling — but it should not be ported wholesale.

The right move: adapt the Pi interface ideas against the current English
`memory` core. `mirror` becomes dual-interface; `mirror-pi` is a reference,
not the source.

---

### `mirror` stays local-first; client-server is a future/parallel track

**Date:** 2026-04-17

Alisson's `mirror-mind` is a greenfield server version with bearer token auth
and a web interface. That is a valid and separate direction.

`mirror` is the mature local runtime. Making it model/runtime agnostic
(Pi support, CV1) does not require adding a server. Client-server remains a
future track or a parallel project — not a CV1 concern.

---

### Skill logic extraction is a prerequisite for Pi

**Date:** 2026-04-17  
**Reference:** Briefing D8

Pi skills cannot be thin wrappers until the shared `src/memory/skills/` modules
exist. CV1.E1 (Shared Command Core) must complete before CV1.E2 (Pi Skill
Surface) can begin. This sequencing is explicit in the CV1 roadmap.

---

### Documentation scaffold before Pi implementation

**Date:** 2026-04-17

Adopted the planning and documentation style from Alisson's `mirror-mind` repo.
The docs scaffold (index, briefing, decisions, roadmap, principles, process) is
created before writing any CV1 code. This gives every future story a place to
live: a plan, a test guide, and a verification moment — before a line of
implementation is written.

---

### Skill layer principle: Python/CLI owns DB; Agent owns filesystem; no run.py

**Date:** 2026-04-18  
**Reference:** CV3.E4 Skill Architecture Cleanup

Every skill in both runtimes (Claude Code and Pi) calls `python -m memory <command>` directly from SKILL.md. No `run.py` intermediary exists under `.claude/skills/` or `.pi/skills/`.

The principle: **Python/CLI owns** everything that touches the database — identity, memories, conversations, metadata. **The agent owns** conditional logic, multi-step workflows, and filesystem reading. A `run.py` is only justified if the logic cannot be expressed as a `python -m memory <command>` call — which has not been the case for any skill to date.

Before CV3.E4, skills accumulated `run.py` wrappers that duplicated CLI modules, mixed DB operations with filesystem traversal, and drifted from one another. CV3.E4 eliminated all 23 run.py files across both runtimes, extracted the remaining logic into canonical CLI modules (`cli/build.py`, `cli/journeys.py`, `cli/consult.py`), and moved banner/icon output into `memory.skills.mirror.main()`.

The `mm:build` hybrid illustrates the pattern: `python -m memory build load <slug>` does all DB work and emits `project_path` as its final output line; Claude Code then reads the docs directory natively using its file tools. Neither side duplicates the other's capability.

---

### CV4 direction: framework/user separation with user homes under `~/.mirror/<user>`

**Date:** 2026-04-18

The next roadmap capability after CV3 is **CV4 — Framework/User Separation**. Mirror Mind should evolve from a repo that contains one user's live identity into a reusable framework with user-owned homes outside the repo.

Target direction:
- the repository keeps only generic identity templates under `templates/identity/`
- real user identity lives under `~/.mirror/<user>/identity/`
- runtime state lives beside it in `~/.mirror/<user>/memory.db`
- default subdirectories `backups/` and `exports/` also live under the user home, but remain configurable to other locations
- legacy Portuguese-era assets (for example `memoria.db`) migrate into this user-home layout

This decision resolves the previously open `MIRROR_USER_DIR` discussion in principle. The implementation details still belong to CV4 planning and stories, but the architectural direction is now set: framework in the repo, real identity and runtime state in the user home.

`uv` is explicitly out of scope for CV4. It may be revisited later as a tooling improvement, but it is not part of the framework/user separation capability.

---

## Open Discussions

### Migration rehearsal — long-term status

**Status:** Open  
**Raised:** 2026-04-17

`src/memory/cli/migration_rehearsal.py` and its tests exist to allow safe dry-run
testing of database migrations. It was built during the English migration to
validate schema changes without touching production.

Question: should this stay permanently? Or should it be removed once the
English migration is clearly stable and the upgrade path for old databases is
no longer a concern?

**Why not urgent:** The cost of keeping it is low. The risk of removing it
prematurely is higher. Revisit when Vinícius decides old database upgrade
support is no longer needed.

---

### User-home selection and runtime-state direction were finalized in CV4

**Date:** 2026-04-19

The CV4 implementation settled the operational details that were still open on
2026-04-18.

Final direction:
- the active user is selected explicitly via CLI override first, then
  `MIRROR_HOME`, then `MIRROR_USER`
- conflicting `MIRROR_HOME` and `MIRROR_USER` values fail hard
- user-scoped commands accept `--mirror-home` where explicit single-home
  targeting matters
- in production, both the default runtime database path and `MEMORY_DIR`-derived
  runtime-state files default under the resolved mirror home
- transcript export is user-scoped, outside the repo by default, and automatic
  export is opt-in through `TRANSCRIPT_EXPORT_AUTOMATIC`

This closes the earlier open discussion about user-home selection/profile
bootstrap details as a CV4 planning question. Future work may refine the UX,
but the architectural and operational direction is no longer open.

---

### CLI parsing consistency and future `argparse` adoption

**Status:** Open  
**Raised:** 2026-04-18

Several commands already use `argparse`, while some older entry points still
parse `sys.argv` directly. Long term, the CLI surface should be standardized on
`argparse` for consistency, clearer help text, safer option parsing, and easier
command evolution.

This is worth doing, but not as opportunistic churn during CV4 feature work.
Revisit it during a future CLI/tooling modernization pass. That pass may happen
near other tooling discussions (for example `uv`), but the decisions should not
be artificially coupled.

---

**See also:** [Briefing](briefing.md) · [Roadmap](roadmap/index.md) · [Worklog](../process/worklog.md)
