[< CV8 Runtime Expansion](../index.md)

# CV8.E1 — Gemini CLI Runtime Spike

**Epic:** Discover Gemini CLI's runtime model and map it against the Mirror Mind runtime contract
**Status:** Done
**Depends on:** Existing runtime contract, Claude Code and Pi reference implementations

---

## What This Is

Before writing a Gemini CLI adapter, we inspected what Gemini CLI actually
exposes. The central question is not "can we call Python from Gemini CLI?" The
central question is whether Gemini CLI can satisfy Mirror Mind's runtime lifecycle:

- session start
- user prompt logging
- assistant response logging or transcript backfill
- session end
- backup
- Mirror Mode pre-response context injection
- native command/skill surface

This spike answers every question. Target parity: **L4 Full Parity**.

---

## Gemini CLI Version

**0.38.2** — installed at `/opt/homebrew/bin/gemini` via Homebrew.

---

## Hook System

Gemini CLI has a full lifecycle hook system. Hooks are shell commands registered
in `.gemini/settings.json` (project-level) or `~/.gemini/settings.json` (user-level).
Communication: JSON on stdin → JSON on stdout. Stderr for logs only. Exit 0 =
success; exit 2 = hard block; other = warning (non-fatal).

Every hook receives these fields on stdin:

```json
{
  "session_id": "<uuid>",
  "transcript_path": "<absolute path to session JSON>",
  "cwd": "<working directory>",
  "hook_event_name": "<event name>",
  "timestamp": "<ISO 8601>"
}
```

`$GEMINI_SESSION_ID` is also available as an **environment variable** inside
every hook script — no stdin parsing required for session identification.

### Lifecycle events and Mirror Mind mapping

| Gemini CLI Event | Fires when | Mirror Mind mapping |
|---|---|---|
| `SessionStart` | Session begins (startup, resume, `/clear`) | `conversation-logger session-start` |
| `BeforeAgent` | After user submits prompt, before model planning | `conversation-logger log-user` + Mirror Mode injection |
| `AfterAgent` | When agent loop ends (final response ready) | `conversation-logger log-assistant` |
| `SessionEnd` | CLI exits or session is cleared | `session-end-pi` + backup (best-effort — see below) |
| `BeforeTool` | Before any tool executes | Not required for Mirror Mind |
| `AfterTool` | After any tool executes | Not required for Mirror Mind |
| `BeforeModel` | Before LLM request is sent | Not required for Mirror Mind |
| `AfterModel` | After each LLM response chunk | Not required for Mirror Mind |
| `PreCompress` | Before context compression | Not required for Mirror Mind |

### SessionEnd limitation

`SessionEnd` is **best-effort**: the CLI exits without waiting for the hook to
complete. This means extraction at session end is unreliable. Decision: use
deferred extraction — `session-end-pi <session_id>` marks the conversation
closed; extraction runs on the next `session-start`. This is identical to how
Pi handles extraction, and is already battle-tested.

---

## Session ID

Stable UUID per session. Available in two ways:

1. `$GEMINI_SESSION_ID` environment variable — available in every hook script
2. `session_id` field in hook stdin JSON

Format: `b0ccfd8b-c2fc-4cd5-bdfc-54f47f407cb3`

No fallback needed. The session ID is always present and stable for the duration
of a session.

---

## Transcript

Full session transcript available at `transcript_path` (in every hook's stdin).
Structure:

```json
{
  "sessionId": "<uuid>",
  "projectHash": "<hash>",
  "startTime": "<ISO 8601>",
  "lastUpdated": "<ISO 8601>",
  "messages": [
    {
      "id": "<uuid>",
      "timestamp": "<ISO 8601>",
      "type": "user",
      "content": [{ "text": "<prompt text>" }]
    },
    {
      "id": "<uuid>",
      "timestamp": "<ISO 8601>",
      "type": "gemini",
      "content": "<response text>",
      "thoughts": [...],
      "tokens": { "input": 0, "output": 0, ... },
      "model": "<model name>",
      "toolCalls": [...]
    }
  ]
}
```

Transcript location: `~/.gemini/tmp/<project-name>/chats/session-<timestamp>-<short-id>.json`

The transcript is written by Gemini CLI as the session progresses and is readable
at session end. This makes transcript backfill possible — same model as Claude Code.

However: since `AfterAgent` fires per turn with `prompt_response` in the hook
input, explicit per-turn assistant logging is available and preferred over
transcript backfill. This is the Pi model. We use explicit per-turn logging.

---

## Mirror Mode Context Injection

`BeforeAgent` → `hookSpecificOutput.additionalContext` — text appended to the
prompt for that turn only, before the model processes it.

This is **automatic per-turn injection**: the `BeforeAgent` hook runs `mirror load`
and returns the identity block as `additionalContext`. The model sees identity
context on every turn without any explicit user invocation.

This is cleaner than Pi (which requires explicit `/mm-mirror` to load context)
and equivalent to Claude Code's `UserPromptSubmit` injection.

Output format:

```json
{
  "hookSpecificOutput": {
    "additionalContext": "<identity block text>"
  }
}
```

Mirror Mode injection is conditional: only fire when the session is in Mirror Mode
(mirror state flag in the database). Builder Mode turns skip the injection.

---

## Skills

Gemini CLI has native SKILL.md discovery. Skills are located in:

1. `.gemini/skills/<name>/SKILL.md` — workspace-local (committed to repo)
2. `~/.gemini/skills/<name>/SKILL.md` — user-global
3. Extension skills

The skill format is identical to Pi's SKILL.md with `name` and `description` frontmatter.
The model activates skills on demand via the `activate_skill` tool.

Mirror Mind's existing Pi skills (`.pi/skills/mm-*/SKILL.md`) can be adapted directly
— same format, same invocation model.

---

## Custom Commands

TOML files in `.gemini/commands/` (project) or `~/.gemini/commands/` (user).
Invoked as `/command-name` or `/namespace:command-name`.

Format:

```toml
description = "Brief description shown in /help"
prompt = "Prompt text, optionally with {{args}} and !{shell commands}"
```

Custom commands are the equivalent of explicit skill invocations. For Mirror Mind,
the skills model is preferred (progressive disclosure, on-demand activation).

---

## Configuration

Project-level configuration: `.gemini/settings.json`

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "name": "mirror-session-start",
            "type": "command",
            "command": "$GEMINI_PROJECT_DIR/.gemini/hooks/session-start.sh"
          }
        ]
      }
    ],
    "BeforeAgent": [...],
    "AfterAgent": [...],
    "SessionEnd": [...]
  }
}
```

Environment variables available in hooks:
- `GEMINI_PROJECT_DIR` — absolute path to project root
- `GEMINI_SESSION_ID` — current session UUID
- `GEMINI_CWD` — current working directory

---

## Parity Assessment

| Level | Name | Status | Notes |
|-------|------|--------|-------|
| L0 | CLI-assisted | ✅ | Can call `uv run python -m memory ...` from any hook or command |
| L1 | Logged runtime | ✅ | `BeforeAgent` (log-user) + `AfterAgent` (log-assistant) + `SessionStart` (session-start) + `$GEMINI_SESSION_ID` |
| L2 | Command surface | ✅ | `.gemini/skills/mm-*/SKILL.md` — same format as Pi, native SKILL.md discovery |
| L3 | Mirror Mode runtime | ✅ | `BeforeAgent` `additionalContext` — automatic injection, no explicit user command needed |
| L4 | Full parity | ✅ | All of the above + isolated smoke test + docs |

**Target parity: L4.**

Only honest limitation: `SessionEnd` is best-effort. Mitigated by deferred extraction (same as Pi).

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV8.E1.S1 | Inspect Gemini CLI extension, command, hook, and transcript capabilities | Done |
| CV8.E1.S2 | Map Gemini CLI lifecycle to the runtime contract | Done |
| CV8.E1.S3 | Decide Gemini CLI target parity level and document limitations | Done |

All three stories completed in a single spike session. Findings documented here.
CV8.E1.S4 (draft implementation plan) is delivered as CV8.E2.

---

## See also

- [CV8.E2 Gemini CLI Runtime Implementation](../cv8-e2-gemini-cli-runtime-implementation/index.md)
- [Runtime Interface Contract](../../../../product/specs/runtime-interface/index.md)
- [Hooks reference](https://geminicli.com/docs/hooks/reference)
