[< CV3.E2 Pi Skill Wrappers](../index.md)

# CV3.E2.S1 — Plan: Port system skills to Pi

## Skills: backup, mute, new, seed, help

All five are SKILL.md-only — no argument forwarding needed. The agent reads
the SKILL.md and calls the appropriate CLI command directly.

| Pi skill | CLI command |
|----------|------------|
| mm-backup | `python -m memory backup` |
| mm-mute | `python -m memory conversation-logger status/mute/unmute` |
| mm-new | `python -m memory conversation-logger switch` + `python -m memory mirror deactivate` |
| mm-seed | `python -m memory seed` |
| mm-help | lists all Pi commands (documentation only) |

## Changes

Create `.pi/skills/mm-<name>/SKILL.md` for each of the five skills.
No `run.py` required.

## Note on mm-new

`mm:new` in Claude Code also calls `python3 .claude/skills/mm:mirror/run.py deactivate`.
The Pi equivalent calls `python -m memory mirror deactivate`, which already exists.
