[< Project](briefing.md)

# Runtime Interface Contract

A **runtime** is any frontend that presents the mirror to the user. Currently
three runtimes exist: Claude Code (hooks), Pi (TypeScript extension), and
Gemini CLI (shell hooks). This document defines what every runtime must
implement to integrate correctly with the Python `memory` core.

The Python CLI (`python -m memory ...`) is the stable interface. Inside this
repo, run it as `uv run python -m memory ...`. Runtimes are thin dispatchers —
they translate lifecycle events into CLI commands and do nothing else. A new
runtime built solely from this document will work.

---

## Lifecycle Events

Every runtime must handle four events. The table below lists the event, the
required CLI command, and any arguments the runtime must supply.

| Event | Required CLI command | Arguments supplied by runtime |
|-------|---------------------|-------------------------------|
| Session start | `uv run python -m memory conversation-logger session-start` | none |
| User prompt | `uv run python -m memory conversation-logger log-user <session_id> <prompt> --interface <name>` | `session_id`, `prompt text`, `interface name` |
| Assistant response | see note below | — |
| Session end | `uv run python -m memory conversation-logger session-end` or `session-end-pi <id>` | see note below |
| Backup | `uv run python -m memory backup --silent` | none |

Backup runs at session end immediately after the session-end command.

---

## Event Details

### Session Start

Runs once when the runtime initialises. Unmutes logging, closes stale orphan
conversations (idle > 30 min), and extracts memories from any conversations
that ended without extraction.

```
uv run python -m memory conversation-logger session-start
```

No arguments. Prints a summary string (may be empty).

---

### User Prompt

Runs before each model turn. Persists the user message to the database.

```
uv run python -m memory conversation-logger log-user <session_id> <prompt> --interface <name>
```

- `session_id` — opaque identifier for the current agent session, supplied by
  the runtime environment
- `prompt` — full text of the user message; truncate at ~50 KB if needed
- `--interface` — runtime name used for attribution (e.g. `claude_code`, `pi`)

Skip if the prompt begins with `/` (skill invocation, not a conversational message).

---

### Assistant Response

Runtimes differ here by design. The difference is structural, not accidental:
Claude Code has access to the full session transcript; Pi logs messages
explicitly as they arrive.

**Pi** — logs each assistant turn explicitly at `agent_end`:

```
uv run python -m memory conversation-logger log-assistant <session_id> <content> --interface pi
```

Collect all assistant messages from the turn, concatenate, and log once.
Truncate at ~50 KB.

**Claude Code** — backfills from the JSONL transcript at session end via
`hook_session_end()`. No per-turn call is needed.

A new runtime should use whichever model matches its architecture: explicit
per-turn logging (like Pi) if messages are available as events; transcript
backfill (like Claude Code) if a session transcript file is available.

---

### Session End

Closes the conversation record. Runtimes differ on extraction timing:

**Claude Code** — has `session_id` and `transcript_path` from the environment.
Extracts memories immediately and backfills assistant messages from the
transcript.

```
uv run python -m memory conversation-logger session-end
```

Input: JSON on stdin — `{"session_id": "<id>", "transcript_path": "<path>"}`.
Claude Code's `Stop` hook provides this via stdin automatically.

**Pi** — does not have transcript access. Defers extraction to the next
`session-start`.

```
uv run python -m memory conversation-logger session-end-pi <session_id>
```

**Gemini CLI** — `SessionEnd` is best-effort (CLI exits without waiting for the
hook). Uses `session-end-pi` for deferred extraction, same as Pi.

```
uv run python -m memory conversation-logger session-end-pi <session_id>
```

A new runtime should use `session-end-pi` unless it can supply a transcript
path, in which case `session-end` gives immediate extraction.

---

## Optional: Mirror Mode Identity Injection

Mirror Mode runtimes inject identity context before the model responds. This
is optional — a runtime that does not support Mirror Mode skips this entirely.

```
uv run python -m memory mirror load --context-only --query "<user prompt>" [--persona <id>] [--journey <id>] [--org] [--session-id <id>]
```

- `--context-only` — loads identity without starting a new database session
  (the model skill starts the session)
- `--query` — used for attachment search; pass the user's full prompt
- `--persona`, `--journey`, `--org` — optional; omit to let auto-detection decide
- `--session-id` — optional but preferred when the runtime has an explicit session identifier; enables session-scoped mirror state and routing

The command prints the identity block. The runtime injects this as a system
note before the model sees the prompt.

**Claude Code** runs this synchronously in `mirror-inject.sh` on
`UserPromptSubmit`, triggered when the prompt begins with `/mm:mirror` or when
Mirror Mode is already active.

**Pi** does not auto-inject. The `/mm-mirror` skill calls `mirror load`
explicitly at the start of each Mirror Mode response.

**Gemini CLI** runs this in the `BeforeAgent` hook. When Mirror Mode is active,
the hook calls `mirror load --context-only` and returns the identity block as
`hookSpecificOutput.additionalContext` — injected automatically before the model
processes the prompt.

---

## Reference Implementations

### Claude Code

| Event | Hook file | Claude Code trigger |
|-------|-----------|---------------------|
| Session start | `.claude/hooks/session-start.sh` | `SessionStart` |
| User prompt | `.claude/hooks/log-user-prompt.sh` | `UserPromptSubmit` |
| Mirror inject | `.claude/hooks/mirror-inject.sh` | `UserPromptSubmit` |
| Session end + backup | `.claude/hooks/log-session-end.sh` | `Stop` |

Hook files are registered in `.claude/settings.json`.

Current external-skill surfacing path:
- keep the installed source/runtime artifacts under `~/.mirror/<user>/...`
- explicitly project installed Claude external skills into a project-local
  `.claude/skills/` surface with:

```bash
uv run python -m memory extensions expose-claude \
  --mirror-home ~/.mirror/<user> \
  --target-root /path/to/project
```

- remove the projected Claude external skill surface later with:

```bash
uv run python -m memory extensions clean-claude \
  --target-root /path/to/project
```

This creates project-visible skill directories such as:

```text
/path/to/project/.claude/skills/ext:review-copy/SKILL.md
/path/to/project/.claude/skills/extensions.external.json
```

Claude no longer relies on a repo-local `mm:review-copy` compatibility skill;
`review-copy` should now be surfaced as an installed external Claude skill.

### Pi

| Event | Extension file | Pi trigger |
|-------|---------------|------------|
| Session start | `.pi/extensions/mirror-logger.ts` | `session_start` |
| User prompt | `.pi/extensions/mirror-logger.ts` | `before_agent_start` |
| Assistant response | `.pi/extensions/mirror-logger.ts` | `agent_end` |
| Session end + backup | `.pi/extensions/mirror-logger.ts` | `session_shutdown` |
| Mirror load | `.pi/skills/mm-mirror/SKILL.md` | `/mm-mirror` skill invocation |

### Gemini CLI

| Event | Hook file | Gemini CLI trigger |
|-------|-----------|--------------------|
| Session start | `.gemini/hooks/session-start.sh` | `SessionStart` |
| User prompt + Mirror inject | `.gemini/hooks/log-user.sh` | `BeforeAgent` |
| Assistant response | `.gemini/hooks/log-assistant.sh` | `AfterAgent` |
| Session end + backup | `.gemini/hooks/session-end.sh` | `SessionEnd` (best-effort) |

Hook files are registered in `.gemini/settings.json`. Session ID is available
as `$GEMINI_SESSION_ID` in every hook environment. Mirror Mode injection uses
`BeforeAgent` `hookSpecificOutput.additionalContext` — automatic per-turn
injection without explicit user invocation.

Skills are discovered from `.gemini/skills/mm-*/SKILL.md` (symlinked from
`.pi/skills/mm-*/`). The SKILL.md format is identical between Pi and Gemini CLI.

---

## External Skill Runtime Surface Contract

External skills are installed into a user-owned source tree under:

```text
~/.mirror/<user>/extensions/<id>/
```

Runtime-facing materialization happens separately under:

```text
~/.mirror/<user>/runtime/skills/<runtime>/
```

For prompt-skills, the materialized shape is:

```text
~/.mirror/<user>/runtime/skills/pi/ext-review-copy/SKILL.md
~/.mirror/<user>/runtime/skills/pi/extensions.json
```

or, for Claude:

```text
~/.mirror/<user>/runtime/skills/claude/ext:review-copy/SKILL.md
~/.mirror/<user>/runtime/skills/claude/extensions.json
```

### `extensions.json` v1

Each runtime root contains an explicit catalog with this shape:

```json
{
  "schema_version": "1",
  "runtime": "pi",
  "target_root": "~/.mirror/<user>/runtime/skills/pi",
  "generated_at": "2026-04-21T18:00:00+00:00",
  "extensions": [
    {
      "id": "review-copy",
      "name": "Review Copy",
      "category": "extension",
      "kind": "prompt-skill",
      "summary": "Multi-LLM copy review workflow that generates a structured HTML report",
      "runtime": "pi",
      "command_name": "ext-review-copy",
      "source_extension_dir": "~/.mirror/<user>/extensions/review-copy",
      "manifest_path": "~/.mirror/<user>/extensions/review-copy/skill.yaml",
      "source_skill_path": "~/.mirror/<user>/extensions/review-copy/SKILL.md",
      "installed_skill_path": "~/.mirror/<user>/runtime/skills/pi/ext-review-copy/SKILL.md"
    }
  ]
}
```

### Consumption rule

Runtimes should treat `runtime/skills/<runtime>/` plus `extensions.json` as the
canonical installed external skill surface. They should not inspect
`~/.mirror/<user>/extensions/` directly during execution.

This keeps:
- authoring/source files separate from runtime materialization
- runtime loading deterministic
- installation and removal explicit

### Pi runtime consumption prep

Pi should prepare to consume the installed external skill surface with this
algorithm:

1. Resolve the active mirror home
2. Read `~/.mirror/<user>/runtime/skills/pi/extensions.json`
3. Validate:
   - `schema_version == "1"`
   - `runtime == "pi"`
4. For each item in `extensions`:
   - trust `command_name` as the runtime-visible command
   - trust `installed_skill_path` as the materialized skill file
   - ignore the source extension tree during execution
5. If the catalog is missing or invalid:
   - continue safely with built-in Pi skills only
   - do not fail session logging or Mirror Mode hooks

Recommended first integration behavior:
- built-in Pi skills remain the default surface
- external skills are additive
- runtime catalog load failures should be logged, not fatal

Current prototype status:
- `.pi/extensions/mirror-logger.ts` now reads the installed Pi runtime catalog on
  `session_start`
- it validates `schema_version` and `runtime`
- it logs discovered external skill commands
- it surfaces a lightweight status hint in the Pi UI (`ext N`)
- on `resources_discover`, it returns installed `SKILL.md` paths from the Pi
  runtime catalog as dynamic `skillPaths`
- this makes installed external Pi skills part of Pi's discovered skill surface
  without re-reading source manifests at runtime

---

## CLI Reference

All commands assume the `memory` package is installed and accessible via
`python -m memory`. Inside this repo, prefer `uv run python -m memory ...` so
commands run inside the locked project environment.

```
uv run python -m memory conversation-logger session-start
uv run python -m memory conversation-logger log-user <session_id> <prompt> --interface <name>
uv run python -m memory conversation-logger log-assistant <session_id> <content> --interface <name>
uv run python -m memory conversation-logger session-end          # reads JSON from stdin
uv run python -m memory conversation-logger session-end-pi <id>  # explicit session id, deferred extraction
uv run python -m memory mirror load --context-only --query <q> [--persona <p>] [--journey <j>] [--org] [--session-id <id>]
uv run python -m memory backup --silent
```

---

**See also:** [CV2 Runtime Portability](roadmap/cv2-runtime-portability/index.md) · [Briefing](briefing.md)
