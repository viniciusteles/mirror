[< CV3 Pi Skill Parity](../index.md)

# CV3.E4 — Skill Architecture Cleanup

**Epic:** All skills call `python -m memory <command>` directly — no run.py intermediaries  
**Status:** ✅  
**Prerequisite:** CV3.E1, CV3.E2, CV3.E3 complete

---

## What This Is

CV3.E1–E3 achieved skill parity but left structural inconsistency behind:

- run.py files that duplicate CLI modules created in E1
- Old-style dispatch (`python3 -m memory.cli.X`) instead of `python -m memory X`
- Skills calling sibling run.py files instead of the CLI
- One skill (mm:build) with a run.py that mixes DB operations with filesystem traversal

This epic enforces the principle discovered during review:

> **Python/CLI owns** everything touching the DB (identity, memories, conversations, metadata).  
> **Agent owns** conditional logic, multi-step workflows, and filesystem reading.  
> **No run.py** unless logic cannot be expressed as a `python -m memory <command>` call.

Under this principle, no skill in either runtime should need a run.py. Claude Code and Pi
both become pure dispatchers to the CLI.

---

## Done Condition

- No run.py files exist under `.claude/skills/` or `.pi/skills/`
- Every skill calls `python -m memory <command>` directly from SKILL.md
- Old-style `python3 -m memory.cli.*` dispatch is gone from all SKILL.md files
- `python -m memory journeys` exists and is used by both runtimes
- `python -m memory mirror load/log` includes the stderr banners previously in run.py
- `python -m memory build load <slug>` handles DB-only context and emits project_path;
  Claude Code reads docs natively via its file tools
- `python -m memory journey set-path <slug> <path>` exists for build set-path
- All existing tests pass

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV3.E4.S1 | SKILL.md dispatch fixes (stale paths, no Python) | ✅ |
| CV3.E4.S2 | Drop redundant run.py (CLI already exists, 18 skills) | ✅ |
| CV3.E4.S3 | New CLI work + drop run.py (journeys, mirror, build) | ✅ |

S1 and S2 can run in parallel. S3 requires new Python work and should be planned separately.

---

## Skills Affected

### S1 — SKILL.md dispatch fixes only

| Skill | Runtime | Problem |
|-------|---------|---------|
| mm:backup | Claude | `python3 -m memory.cli.backup` → `python -m memory backup` |
| mm:mute | Claude | `python3 -m memory.cli.conversation_logger` → `python -m memory conversation-logger` |
| mm:new | Claude | old-style logger + `mm:mirror/run.py deactivate` → clean CLI calls |
| mm:review-copy | Claude | historical cleanup target; later migrated out of the repo and replaced by the external `ext:review-copy` path |
| mm-review-copy | Pi | historical cleanup target; later migrated out of the repo and replaced by the external `ext-review-copy` path |

### S2 — Delete run.py (CLI already exists)

| Skill | Runtime | CLI command |
|-------|---------|------------|
| mm:consult | Claude | `python -m memory consult` |
| mm:conversations | Claude | `python -m memory conversations` |
| mm:journal | Claude | `python -m memory journal` |
| mm:journey | Claude | `python -m memory journey` |
| mm:memories | Claude | `python -m memory memories` |
| mm:recall | Claude | `python -m memory recall` |
| mm:save | Claude | `python -m memory save` |
| mm:tasks | Claude | `python -m memory tasks` |
| mm:week | Claude | `python -m memory week` |
| mm-consult | Pi | `python -m memory consult` |
| mm-conversations | Pi | `python -m memory conversations` |
| mm-journal | Pi | `python -m memory journal` |
| mm-journey | Pi | `python -m memory journey` |
| mm-memories | Pi | `python -m memory memories` |
| mm-recall | Pi | `python -m memory recall` |
| mm-save | Pi | `python -m memory save` |
| mm-tasks | Pi | `python -m memory tasks` |
| mm-week | Pi | `python -m memory week` |

### S3 — New CLI work required

| Skill | Runtime | Work |
|-------|---------|------|
| mm:journeys | Claude | Create `python -m memory journeys`; drop run.py |
| mm-journeys | Pi | Same CLI; drop run.py |
| mm:mirror | Claude | Move stderr banners into `memory.skills.mirror.main()`; drop run.py |
| mm:build | Claude | Create `python -m memory build load <slug>` (DB-only, emits project_path); add `python -m memory journey set-path`; drop run.py |

---

**See also:** [CV3 Pi Skill Parity](../index.md) · [CV3.E3 Pi Intelligence Skills](../cv3-e3-pi-intelligence-skills/index.md)
