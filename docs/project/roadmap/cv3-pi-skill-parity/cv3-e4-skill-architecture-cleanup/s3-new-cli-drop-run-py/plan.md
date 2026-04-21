[< CV3.E4 Skill Architecture Cleanup](../index.md)

# CV3.E4.S3 — New CLI Work + Drop run.py

**Story:** Create missing CLI commands, then drop the last three run.py files  
**Status:** ✅

---

## What This Is

Three skills have run.py files with logic that has no CLI equivalent yet.
Each requires new Python work before the run.py can be deleted.

---

## Part A — `python -m memory journeys`

### Problem

`mm:journeys/run.py` (Claude) has a rich implementation: reads journey identity
from DB, extracts status and stage via regex, formats with icons and descriptions.
The Pi skill's run.py calls `memory.skills.mirror.main(["journeys"])` which returns
simpler output. Neither maps cleanly to an existing CLI command.

### Solution

Create `src/memory/cli/journeys.py` by extracting the logic from
`.claude/skills/mm:journeys/run.py`. Wire as `python -m memory journeys` in
`__main__.py`. Both runtimes drop their run.py and call the CLI directly.

### Files

| File | Action |
|------|--------|
| `src/memory/cli/journeys.py` | New — extracted from mm:journeys/run.py |
| `src/memory/__main__.py` | Add `journeys` branch + USAGE entry |
| `.claude/skills/mm:journeys/run.py` | Delete |
| `.claude/skills/mm:journeys/SKILL.md` | Update: `python -m memory journeys` |
| `.pi/skills/mm-journeys/run.py` | Delete |
| `.pi/skills/mm-journeys/SKILL.md` | Update: `python -m memory journeys` |

---

## Part B — Mirror banners into the module

### Problem

`mm:mirror/run.py` wraps `memory.skills.mirror` with ANSI stderr banners and
persona icons. `python -m memory mirror` dispatches to `memory.skills.mirror.main()`
but without the banners — so the output differs from what the skill produces today.

### Solution

Move the banner logic (`_print_mirror_banner`, `PERSONA_ICONS`, journey detection
output) into `memory.skills.mirror.main()`. Once the module produces the same
output, SKILL.md can call `python -m memory mirror load/log` directly. The hook
`mirror-inject.sh` already uses this form, so no hook changes needed.

### Files

| File | Action |
|------|--------|
| `src/memory/skills/mirror.py` | Add banner/icon output to `main()` |
| `.claude/skills/mm:mirror/run.py` | Delete |
| `.claude/skills/mm:mirror/SKILL.md` | Update: `python -m memory mirror load/log` |

---

## Part C — Build hybrid approach

### Problem

`mm:build/run.py` mixes DB operations with filesystem traversal (reading project
docs from `<project_path>/docs/`). Under the principle, Python owns DB; Claude
owns filesystem. The run.py should not exist.

### Solution

**`load` subcommand:** Create `python -m memory build load <slug>` that does
only the DB work:
1. Load mirror context (`persona=engineer`, `journey=slug`)
2. Search and emit relevant memories
3. Switch conversation to engineer/slug
4. Emit the `project_path` as the final line

SKILL.md then instructs Claude to: run `python -m memory build load <slug>`,
read the project_path from output, then read the docs directory using its native
file tools (Glob + Read).

**`set-path` subcommand:** Add `python -m memory journey set-path <slug> <path>`
to the existing `journey` CLI — it's a journey metadata operation and belongs there.

**`log` subcommand:** Use `python -m memory conversation-logger log-assistant
"<text>"` — add this subcommand to the conversation-logger CLI if it doesn't exist,
or reuse an existing mechanism.

### Files

| File | Action |
|------|--------|
| `src/memory/cli/build.py` | New — DB-only load + emit project_path |
| `src/memory/cli/journey.py` | Add `set-path` subcommand |
| `src/memory/cli/conversation_logger.py` | Add `log-assistant` subcommand if needed |
| `src/memory/__main__.py` | Add `build` branch + USAGE entry |
| `.claude/skills/mm:build/run.py` | Delete |
| `.claude/skills/mm:build/SKILL.md` | Rewrite: two-step load (CLI + native file read) + updated set-path/log commands |
| `.pi/skills/mm-mirror/run.py` | Delete (thin wrapper; same module as Claude) |
| `.pi/skills/mm-mirror/SKILL.md` | Update to `python -m memory mirror load/log` |

---

## Done Condition

- `python -m memory journeys` works; both mm:journeys and mm-journeys call it directly
- `python -m memory mirror load` emits banners; mm:mirror SKILL.md calls it directly
- `python -m memory build load <slug>` emits project_path; SKILL.md delegates filesystem to Claude
- `python -m memory journey set-path <slug> <path>` works
- Zero run.py files remain under `.claude/skills/` and `.pi/skills/`
- All existing tests pass
