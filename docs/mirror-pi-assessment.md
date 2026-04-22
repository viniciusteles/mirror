# Mirror Pi Assessment

Date: 2026-04-17

This assessment compares the current `mirror` repository with the Pi-adapted
version at `~/dev/workspace/mirror-pi`. The goal is to understand how to adapt
the current English `mirror` runtime to run on Pi without depending on
Claude Code specifically.

## Summary

The adaptation path is clear, but `mirror-pi` should not be ported wholesale
into `mirror`.

`mirror-pi` is useful as a working spike, but it is pre-English-migration and
still uses `memoria`, `travessia`, `.espelho`, and related Portuguese runtime
language. The right move is to port the Pi interface ideas, not the old memory
core.

The current `mirror` already has the better core:

- English `memory` package
- English schema/runtime vocabulary
- current identity YAMLs
- better Claude hooks
- current `.claude/skills/mm:*`
- tested migration boundaries

The plan should be to make `mirror` dual-interface: Claude Code plus Pi.

## What Mirror Pi Adds

The useful pieces in `~/dev/workspace/mirror-pi` are:

- `.pi/settings.json`: enables Pi skill commands.
- `.pi/extensions/mirror-logger.ts`: Pi lifecycle integration.
- `.pi/skills/*`: Pi-compatible skill names, such as `mm-mirror` instead of
  Claude's `mm:mirror`.
- `memoria/conversation_logger.py`: extra Pi session handling: `session-start`,
  stale orphan closing, pending extraction, Pi JSONL backfill, and
  `--interface pi`.

## Recommended Plan

### 1. Add a Pi integration skeleton

Create:

```text
.pi/settings.json
.pi/extensions/mirror-logger.ts
.pi/skills/mm-mirror/
.pi/skills/mm-consult/
.pi/skills/mm-journey/
...
```

Use Pi's hyphenated command names:

```text
/mm-mirror
/mm-consult
/mm-journey
/mm-tasks
```

Keep Claude's colon commands unchanged:

```text
/mm:mirror
/mm:consult
/mm:journey
/mm:tasks
```

This avoids breaking the current Claude workflow.

### 2. Extract skill logic out of `.claude/skills`

Right now many Claude skill scripts contain real logic directly under
`.claude/skills/mm:*/run.py`.

For Pi, duplicating those scripts under `.pi/skills/mm-*/run.py` would create
drift. Better:

```text
src/memory/skills/mirror.py
src/memory/skills/consult.py
src/memory/skills/journey.py
src/memory/skills/tasks.py
...
```

Then both interfaces become thin wrappers:

```python
from memory.skills.mirror import main

if __name__ == "__main__":
    main()
```

This is the most important design cleanup. It gives us one implementation and
two frontends.

### 3. Add a real unified CLI

`mirror-pi` has a unified CLI:

```text
memoria mirror load ...
memoria tasks ...
memoria conversation-logger session-start
```

`mirror` currently only has a small `python -m memory seed/list`
dispatcher, while most skill logic is invoked through
`.claude/skills/.../run.py`.

Add either:

```text
python -m memory mirror load ...
python -m memory tasks ...
python -m memory conversation-logger ...
```

or console scripts:

```text
memory mirror load ...
memory tasks ...
memory conversation-logger ...
```

Start with `python -m memory <command>` because it avoids packaging churn. Add a
console script later if useful.

### 4. Port Pi session lifecycle behavior into English `memory`

Port the useful behavior from `mirror-pi`'s `conversation_logger.py`, translated
to current naming:

- `session-start`
- `extract-pending`
- `close_stale_orphans`
- `backfill_pi_sessions`
- `--interface pi` for `log-user` and `log-assistant`
- metadata fields like `pi_session_file` and `backfill_source`

Current `mirror` already has conversation logging, but it is Claude-oriented.
Pi needs lifecycle events because Pi sessions and transcripts live under
`~/.pi/agent/sessions/...`, not `~/.claude/projects/...`.

### 5. Rewrite the Pi extension against current English runtime

Port `mirror-pi/.pi/extensions/mirror-logger.ts`, but change:

```text
~/.espelho           -> ~/.mirror or MEMORY_DIR
memoria              -> memory
travessia            -> journey
Memoria pronta       -> Memory ready
```

The extension should stay thin:

- call Python
- swallow failures
- log diagnostics
- never block Pi if memory logging fails

The extension should dispatch to:

```text
python3 -m memory conversation-logger session-start
python3 -m memory conversation-logger log-user ...
python3 -m memory conversation-logger log-assistant ...
python3 -m memory conversation-logger session-end ...
python3 -m memory backup --silent
```

### 6. Translate/adapt Pi skill docs, not copy them

Use current `.claude/skills/mm:*` English docs as source, then adapt syntax for
Pi.

Claude:

```text
python3 .claude/skills/mm:mirror/run.py load --journey mirror
```

Pi:

```text
python3 .pi/skills/mm-mirror/run.py load --journey mirror
```

or after unified CLI:

```text
python3 -m memory mirror load --journey mirror
```

The Pi skill docs in `mirror-pi` are still Portuguese-domain and should not be
copied directly.

### 7. Handle transcript export/save separately

Current `mm:save` searches Claude transcripts under:

```text
~/.claude/projects
```

Pi needs equivalent discovery under:

```text
~/.pi/agent/sessions
```

Options:

- make `memory.cli.transcript_export` support both Claude and Pi JSONL shapes
- add a small `memory.cli.pi_transcript` helper
- make `mm-save` detect interface from `CURRENT_SESSION_PATH`

This is not required for first smoke, but it is required for feature parity.

### 8. Decide later on external user directories

`mirror-pi` separates framework from user data via:

```text
MIRROR_USER_DIR
users/me/
```

`mirror` currently seeds from in-repo `identity/`.

That is a product/design decision, not required for Pi runtime support. Do not
mix it into the first Pi adaptation. First get Pi running against current
`identity/` and current database. Then decide whether Mirror Mind should become
a reusable framework with private external identity directories.

## Implementation Sequence

Split this into small commits:

1. `Add importable memory skill modules`
2. `Add unified memory CLI commands`
3. `Add Pi conversation logger lifecycle support`
4. `Add Pi skill wrappers`
5. `Add Pi extension for memory logging`
6. `Document Claude and Pi runtime usage`
7. `Validate Mirror Mind on Pi`

## Tests First

Before changing behavior, add focused tests for:

- `conversation_logger log-user --interface pi`
- `conversation_logger log-assistant --interface pi`
- `session-start` unmuting and returning a summary
- stale orphan closing without touching the current session
- Pi JSONL parsing/backfill
- command dispatch through `python -m memory`
- Pi skill wrappers importing the shared `memory.skills.*` modules

Then smoke test with an isolated `HOME`/`MEMORY_DIR`, the same way the English
migration was validated.

## Main Risks

- Session ID shape differs: Claude uses a session id; Pi may give a session file
  path. The `mirror-pi` spike stores paths as session IDs. Make this explicit
  and tested.
- Transcript formats differ: Claude and Pi JSONL are similar but not identical.
- Skill command naming differs: Claude accepts `mm:mirror`; Pi uses `mm-mirror`.
- Duplicated skill code would drift: extracting shared `memory.skills.*` avoids
  that.
- Production database safety: first validation should use temporary `HOME`,
  `MEMORY_DIR`, and `DB_PATH`; no production memory DB mutation without explicit
  confirmation.

## Recommended Next Move

Start with the shared skill-module extraction and unified CLI. That gives a
clean base before adding `.pi` files.
