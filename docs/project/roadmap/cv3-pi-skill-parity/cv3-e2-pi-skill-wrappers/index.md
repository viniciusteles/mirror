[< CV3 Pi Skill Parity](../index.md)

# CV3.E2 — Pi Skill Wrappers

**Epic:** 15 skills available on Pi  
**Status:** ✅ Done  
**Prerequisite:** CV3.E1 complete

---

## What This Is

With the CLI complete, this epic creates the Pi skill wrappers. Each wrapper
follows the same pattern as `.pi/skills/mm-mirror`: a `SKILL.md` describing
what the skill does for the agent, and a `run.py` that dispatches to
`python -m memory <command>`.

Skills without Python logic (backup, mute, new, seed, help) need only a
`SKILL.md` — the agent calls the CLI directly from the skill instructions.

---

## Skills to Port

| Pi skill name | Claude Code equivalent | Dispatch |
|--------------|----------------------|---------|
| mm-backup | mm:backup | `python -m memory backup` |
| mm-mute | mm:mute | `python -m memory conversation-logger mute/unmute/status` |
| mm-new | mm:new | `python -m memory conversation-logger switch` |
| mm-seed | mm:seed | `python -m memory seed` |
| mm-help | mm:help | documentation only |
| mm-journal | mm:journal | `python -m memory journal` |
| mm-journeys | mm:journeys | `python -m memory mirror journeys` |
| mm-journey | mm:journey | `python -m memory journey` |
| mm-memories | mm:memories | `python -m memory memories` |
| mm-conversations | mm:conversations | `python -m memory conversations` |
| mm-recall | mm:recall | `python -m memory recall` |
| mm-tasks | mm:tasks | `python -m memory tasks` |
| mm-week | mm:week | `python -m memory week` |
| mm-save | mm:save | `python -m memory save` |
| mm-build | — | excluded (Claude Code-specific) |

---

## Done Condition

- All 14 skill directories exist under `.pi/skills/`
- Each has a `SKILL.md` accurate to what the skill does on Pi
- Each that needs Python dispatch has a `run.py` calling the CLI
- All Claude Code skill behavior is preserved and tests pass

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV3.E2.S1 | Port system skills: backup, mute, new, seed, help | ✅ |
| CV3.E2.S2 | Port memory skills: journal, memories, conversations, recall, save | ✅ |
| CV3.E2.S3 | Port journey and task skills: journeys, journey, tasks, week | ✅ |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

**See also:** [CV3 Pi Skill Parity](../index.md) · [CV3.E1 CLI Completeness](../cv3-e1-cli-completeness/index.md) · [CV3.E3 Pi Intelligence Skills](../cv3-e3-pi-intelligence-skills/index.md)
