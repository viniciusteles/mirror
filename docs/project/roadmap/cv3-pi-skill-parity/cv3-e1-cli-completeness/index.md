[< CV3 Pi Skill Parity](../index.md)

# CV3.E1 — CLI Completeness

**Epic:** Every skill operation is reachable via `python -m memory`  
**Status:** ✅ Done  
**Prerequisite for:** CV3.E2, CV3.E3

---

## What This Is

Pi wrappers must call `python -m memory <command>`. Before they can be written,
every skill operation needs a CLI command. Currently only five operations are
exposed: `seed`, `list`, `mirror`, `conversation-logger`, `backup`.

This epic adds CLI commands for all remaining skill operations. The Claude Code
skill `run.py` files remain unchanged — they continue to import from `memory.*`
directly. The new CLI commands expose the same logic through a stable interface.

---

## Operations to Expose

| Skill | New CLI command |
|-------|----------------|
| mm:journal | `python -m memory journal <text> [--journey SLUG]` |
| mm:journeys | `python -m memory mirror journeys` (already exists via mirror subcommand — verify) |
| mm:journey | `python -m memory journey status [--journey SLUG]` · `journey update <slug> <field> <value>` |
| mm:memories | `python -m memory memories [--layer L] [--type T] [--journey J] [--limit N]` |
| mm:conversations | `python -m memory conversations [--limit N] [--journey J]` |
| mm:recall | `python -m memory recall <conversation_id>` |
| mm:tasks | `python -m memory tasks [--journey J]` · `tasks create` · `tasks update` (wire existing `cli/tasks.py`) |
| mm:week | `python -m memory week [--show] [--ingest <text>]` |
| mm:save | `python -m memory save [--last-turn] [--output PATH]` |

`mute` and `new` are already reachable via `conversation-logger mute/unmute`
and `conversation-logger switch` — no new commands needed.

---

## Done Condition

- All commands above are implemented and respond correctly
- `python -m memory --help` (or equivalent) lists all new commands
- Each command has unit tests
- All existing tests still pass

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV3.E1.S1 | Add `journal` CLI command | ✅ |
| CV3.E1.S2 | Add `journey` CLI command (status + update) | ✅ |
| CV3.E1.S3 | Add `memories` CLI command | ✅ |
| CV3.E1.S4 | Add `conversations` CLI command | ✅ |
| CV3.E1.S5 | Add `recall` CLI command | ✅ |
| CV3.E1.S6 | Wire `tasks` CLI command (cli/tasks_cmd.py — new file) | ✅ |
| CV3.E1.S7 | Add `week` CLI command | ✅ |
| CV3.E1.S8 | Add `save` CLI command | ✅ |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

**See also:** [CV3 Pi Skill Parity](../index.md) · [CV3.E2 Pi Skill Wrappers](../cv3-e2-pi-skill-wrappers/index.md)
