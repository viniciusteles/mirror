[< CV3.E4 Skill Architecture Cleanup](../index.md)

# CV3.E4.S2 — Drop Redundant run.py

**Story:** Delete 18 run.py files whose logic lives in the CLI package  
**Status:** —

---

## What This Is

CV3.E1 extracted the logic from Claude Code run.py files into proper CLI modules
under `src/memory/cli/`. The run.py files were never updated to thin wrappers —
they still carry the original implementation, duplicating what the package already
provides. This story deletes them and updates SKILL.md to call the CLI directly.

The same pattern applies to Pi: the run.py files there are thin imports that add
no value once SKILL.md calls `python -m memory <command>` directly.

---

## Per-Skill Changes

For each skill below: delete `run.py`, update `SKILL.md` to replace
`python3 .claude/skills/<skill>/run.py` (or `.pi/skills/<skill>/run.py`) with
`python -m memory <command>`.

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

---

## SKILL.md Argument Passthrough

Each updated SKILL.md must pass arguments the same way the run.py did.
Verify the CLI's argparse accepts all flags the skill uses before deleting run.py.

Key cases:
- `mm:journey`: `update <slug> <content>` and stdin (`-`) must work via CLI
- `mm:week`: `view`, `plan "<text>"`, `save` subcommands
- `mm:tasks`: all subcommands (`add`, `done`, `doing`, `block`, `import`, `sync`, `sync-config`, `delete`)
- `mm:save`: optional slug + `--full` flag

---

## Done Condition

- 18 run.py files deleted
- 18 SKILL.md files updated to call `python -m memory <command>` directly
- No orphaned run.py files remain in the affected skill directories
- All existing tests pass
