[< CV1 Pi Runtime](../index.md)

# CV1.E1 — Shared Command Core

**Epic:** The mirror speaks from one place  
**Status:** ✅ Done  
**Prerequisite for:** CV1.E2 (Pi Skill Surface)

---

## What This Is

Right now, all skill logic lives inside `.claude/skills/mm:*/run.py`. Adding Pi
support by copying those scripts into `.pi/skills/mm-*/run.py` would create two
copies of the same logic that will diverge.

This epic extracts the skill logic into importable Python modules under
`src/memory/skills/`, then makes the Claude skill scripts thin wrappers that
call those modules. The Pi wrappers will call the same modules.

It also adds a unified CLI so both interfaces can dispatch commands through
`python -m memory <command>` instead of calling skill scripts directly.

---

## Done Condition

- `src/memory/skills/` contains importable modules for all active skills
- `.claude/skills/mm:*/run.py` are thin wrappers calling `memory.skills.*`
- `python -m memory mirror load --journey <slug>` works
- `python -m memory conversation-logger log-user ...` works
- All existing Claude skill behavior is preserved
- Tests cover the shared modules

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV1.E1.S1 | Extract skill modules into `src/memory/skills/` | ✅ |
| CV1.E1.S2 | Add unified `python -m memory` CLI commands | ✅ |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

**See also:** [CV1 Pi Runtime](../index.md) · [Briefing D8](../../../../project/briefing.md) · [Pi Adoption Spike](../../../../process/spikes/pi-runtime-adoption-2026-04-17.md)
