[< CV3.E2 Pi Skill Wrappers](../index.md)

# CV3.E2.S3 — Plan: Port journey and task skills to Pi

## Skills: journeys, journey, tasks, week

Each gets a `SKILL.md` + `run.py`.

| Pi skill | run.py imports from |
|----------|---------------------|
| mm-journeys | `memory.skills.mirror` (`main(["journeys"])`) |
| mm-journey | `memory.cli.journey` |
| mm-tasks | `memory.cli.tasks_cmd` |
| mm-week | `memory.cli.week` |

`mm-journeys` reuses `memory.skills.mirror.main(["journeys"])` — the compact
list is already implemented there and used by `python -m memory mirror journeys`.

## Changes

Create `.pi/skills/mm-<name>/SKILL.md` and `.pi/skills/mm-<name>/run.py`
for each of the four skills.
