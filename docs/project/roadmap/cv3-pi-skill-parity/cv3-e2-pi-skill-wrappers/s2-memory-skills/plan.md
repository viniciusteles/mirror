[< CV3.E2 Pi Skill Wrappers](../index.md)

# CV3.E2.S2 — Plan: Port memory skills to Pi

## Skills: journal, memories, conversations, recall, save

Each gets a `SKILL.md` + `run.py`. The run.py imports from `memory.cli.*`
and calls `main()` — identical pattern to mm-mirror.

| Pi skill | run.py imports from |
|----------|---------------------|
| mm-journal | `memory.cli.journal` |
| mm-memories | `memory.cli.memories` |
| mm-conversations | `memory.cli.conversations` |
| mm-recall | `memory.cli.recall` |
| mm-save | `memory.cli.save` |

## Note on mm-save

`mm:save` reads Claude Code JSONL transcripts. On Pi, no JSONL exists.
The skill will fail gracefully with "transcript file not found". The SKILL.md
documents this limitation explicitly.

## Changes

Create `.pi/skills/mm-<name>/SKILL.md` and `.pi/skills/mm-<name>/run.py`
for each of the five skills.
