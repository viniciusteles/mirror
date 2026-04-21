[< Project](briefing.md)

# Runtime Interface Contract

A **runtime** is any frontend that presents the mirror to the user. Currently
two runtimes exist: Claude Code (hooks) and Pi (TypeScript extension). This
document defines what every runtime must implement to integrate correctly with
the Python `memory` core.

The Python CLI (`python -m memory ...`) is the stable interface. Runtimes are
thin dispatchers — they translate lifecycle events into CLI commands and do
nothing else. A new runtime built solely from this document will work.

---

## Lifecycle Events

Every runtime must handle four events. The table below lists the event, the
required CLI command, and any arguments the runtime must supply.

| Event | Required CLI command | Arguments supplied by runtime |
|-------|---------------------|-------------------------------|
| Session start | `python -m memory conversation-logger session-start` | none |
| User prompt | `python -m memory conversation-logger log-user <session_id> <prompt> --interface <name>` | `session_id`, `prompt text`, `interface name` |
| Assistant response | see note below | — |
| Session end | `python -m memory conversation-logger session-end` or `session-end-pi <id>` | see note below |
| Backup | `python -m memory backup --silent` | none |

Backup runs at session end immediately after the session-end command.

---

## Event Details

### Session Start

Runs once when the runtime initialises. Unmutes logging, closes stale orphan
conversations (idle > 30 min), and extracts memories from any conversations
that ended without extraction.

```
python -m memory conversation-logger session-start
```

No arguments. Prints a summary string (may be empty).

---

### User Prompt

Runs before each model turn. Persists the user message to the database.

```
python -m memory conversation-logger log-user <session_id> <prompt> --interface <name>
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
python -m memory conversation-logger log-assistant <session_id> <content> --interface pi
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
python -m memory conversation-logger session-end
```

Input: JSON on stdin — `{"session_id": "<id>", "transcript_path": "<path>"}`.
Claude Code's `Stop` hook provides this via stdin automatically.

**Pi** — does not have transcript access. Defers extraction to the next
`session-start`.

```
python -m memory conversation-logger session-end-pi <session_id>
```

A new runtime should use `session-end-pi` unless it can supply a transcript
path, in which case `session-end` gives immediate extraction.

---

## Optional: Mirror Mode Identity Injection

Mirror Mode runtimes inject identity context before the model responds. This
is optional — a runtime that does not support Mirror Mode skips this entirely.

```
python -m memory mirror load --context-only --query "<user prompt>" [--persona <id>] [--journey <id>] [--org] [--session-id <id>]
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

### Pi

| Event | Extension file | Pi trigger |
|-------|---------------|------------|
| Session start | `.pi/extensions/mirror-logger.ts` | `session_start` |
| User prompt | `.pi/extensions/mirror-logger.ts` | `before_agent_start` |
| Assistant response | `.pi/extensions/mirror-logger.ts` | `agent_end` |
| Session end + backup | `.pi/extensions/mirror-logger.ts` | `session_shutdown` |
| Mirror load | `.pi/skills/mm-mirror/SKILL.md` | `/mm-mirror` skill invocation |

---

## CLI Reference

All commands assume the `memory` package is installed and accessible via
`python -m memory`.

```
python -m memory conversation-logger session-start
python -m memory conversation-logger log-user <session_id> <prompt> --interface <name>
python -m memory conversation-logger log-assistant <session_id> <content> --interface <name>
python -m memory conversation-logger session-end          # reads JSON from stdin
python -m memory conversation-logger session-end-pi <id>  # explicit session id, deferred extraction
python -m memory mirror load --context-only --query <q> [--persona <p>] [--journey <j>] [--org] [--session-id <id>]
python -m memory backup --silent
```

---

**See also:** [CV2 Runtime Portability](roadmap/cv2-runtime-portability/index.md) · [Briefing](briefing.md)
