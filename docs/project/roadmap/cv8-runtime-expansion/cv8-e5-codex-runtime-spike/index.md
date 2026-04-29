[< CV8 Runtime Expansion](../index.md)

# CV8.E5 — Codex Runtime Spike

**Epic:** Discover Codex's runtime model and map it against the hardened Mirror Mind runtime contract
**Status:** Done
**Depends on:** CV8.E4 Runtime Adapter Hardening

---

## Codex Version

**0.125.0** — installed at `/opt/homebrew/bin/codex` via Homebrew Cask.

---

## Key Finding: No Lifecycle Hooks

Codex has no `SessionStart`, `BeforeAgent`, `AfterAgent`, or `SessionEnd` hook
system. There is no hook configuration file. This is the central constraint that
bounds the parity level.

Everything else — skills, AGENTS.md injection, JSONL transcript backfill — is
available and works well. But without hooks, automatic per-turn logging and
per-turn dynamic context injection are not possible.

---

## Session ID

Codex writes a JSONL session file per session:

```
~/.codex/sessions/YYYY/MM/DD/rollout-<timestamp>-<uuid>.jsonl
```

The session ID (UUID) is embedded in the filename and in the first line
(`session_meta.payload.id`). It is **not available as an env var** during the
session — only extractable post-hoc from the filename.

A wrapper script can track the start time, wait for `codex` to exit, then find
the newest JSONL written after the start time for the project's `cwd`.

---

## Transcript

Full session JSONL at `~/.codex/sessions/`. Parseable after the session ends.

Relevant message types:

```jsonl
{"type": "event_msg", "payload": {"type": "user_message", "message": "<text>"}}
{"type": "event_msg", "payload": {"type": "agent_message", "message": "<text>"}}
{"type": "session_meta", "payload": {"id": "<uuid>", "cwd": "<path>", ...}}
```

All user and assistant turns are captured. This makes **transcript backfill
possible** — same model as Claude Code, but triggered by a wrapper script at
session end rather than a `Stop` hook.

---

## Skills

Native SKILL.md discovery. Codex scans:

1. `~/.codex/skills/<name>/SKILL.md` — global user skills
2. `.agents/skills/<name>/SKILL.md` — project-local (workspace-committed)

Format is identical to Pi and Gemini CLI SKILL.md (frontmatter `name` and
`description`). Confirmed via `codex debug prompt-input` — project `.agents/skills/`
entries appear in the skills instructions injected into the model context.

Mirror Mind's existing Pi skills are directly reusable via symlinks:

```
.agents/skills/mm-mirror → ../.pi/skills/mm-mirror/
```

**L2 is fully achievable with zero Python changes.**

---

## Context Injection (AGENTS.md)

Codex loads `AGENTS.md` files hierarchically at session start:

1. `~/.codex/AGENTS.md` — global (always loaded)
2. `<project>/AGENTS.md` — project-local (appended, wrapped in `--- project-doc ---`)

Both are concatenated and injected as a `user`-role message before the first
model turn. This is **static session-start injection** — the identity block is
in context from turn 1, but not refreshed per turn.

Confirmed via `codex debug prompt-input`:

```
# AGENTS.md instructions for /path/to/project
<INSTRUCTIONS>
[global ~/.codex/AGENTS.md content]
--- project-doc ---
[project AGENTS.md content]
</INSTRUCTIONS>
```

**Implication for Mirror Mode:**
- A project `AGENTS.md` can include a call to `uv run python -m memory mirror load`
  and instruct the model to treat the output as identity context for the session.
- However, the model executes this at session start, not automatically before
  each turn. This is the **explicit invocation model** — same as Pi.
- No `BeforeAgent`-equivalent hook exists for automatic per-turn injection.

---

## Mirror Mode Context Strategy

Two options for Codex Mirror Mode:

**Option A — AGENTS.md static identity block**
Pre-bake a static identity block into `AGENTS.md` using `mirror load` output.
Requires refreshing `AGENTS.md` each session (wrapper can do this). The model
always has identity in context from turn 1, but it's a snapshot, not live.

**Option B — Explicit skill invocation (Pi model)**
`AGENTS.md` instructs the model to call `uv run python -m memory mirror load`
when the user activates Mirror Mode. The `mm-mirror` skill provides the procedure.
Live, but requires user action.

**Decision: Option B** — same as Pi. Explicit invocation is more reliable
and doesn't require a stale identity snapshot in `AGENTS.md`. The `mm-mirror`
skill handles everything.

---

## Lifecycle Mapping

| Mirror Mind event | Codex mechanism | Notes |
|---|---|---|
| Session start | Wrapper script calls `conversation-logger session-start` before `codex` | No hook; wrapper only |
| User prompt logging | Wrapper backfills from JSONL after session | Not per-turn; end-of-session only |
| Assistant response logging | Wrapper backfills from JSONL after session | Not per-turn; end-of-session only |
| Session end + extraction | Wrapper calls `session-end-pi` + `backup` after `codex` exits | Deferred extraction |
| Mirror Mode injection | `mm-mirror` skill + explicit `/mm-mirror` invocation | Same as Pi |
| Command surface | `.agents/skills/mm-*/SKILL.md` | Native skill discovery |

---

## Parity Assessment

| Level | Name | Status | Notes |
|-------|------|--------|-------|
| L0 | CLI-assisted | ✅ | Can call `uv run python -m memory ...` directly |
| L1 | Logged runtime | ✅ with wrapper | JSONL backfill at session end; not per-turn |
| L2 | Command surface | ✅ | `.agents/skills/mm-*/SKILL.md` — 19 symlinks |
| L3 | Mirror Mode runtime | ✅ | Explicit invocation via `mm-mirror` skill + AGENTS.md |
| L4 | Full parity | ❌ | No per-turn dynamic injection; no session lifecycle hooks |

**Target parity: L3.**

Honest limitations:
- Logging is end-of-session backfill, not per-turn (memory extraction quality
  is the same; just no real-time logging)
- Mirror Mode injection is explicit (`/mm-mirror`), not automatic per-turn
- Session ID requires post-hoc extraction from JSONL filename
- No way to intercept or block turns; hooks are L0 here

---

## Wrapper Script Design

A `codex-mirror` wrapper provides L1+L3 without any hooks:

```bash
#!/usr/bin/env bash
# 1. Mark start time for JSONL detection
START_TIME=$(date -u +%s)

# 2. Session start
uv run python -m memory conversation-logger session-start >/dev/null 2>&1

# 3. Run Codex (blocks until user exits)
codex "$@"

# 4. Find the JSONL created during this session (newest file in project cwd tree)
SESSION_JSONL=$(find ~/.codex/sessions -name "*.jsonl" -newer /tmp/codex-mirror-start \
  | xargs grep -l "\"cwd\":\"$PWD\"" 2>/dev/null | tail -1)

# 5. Extract session ID and backfill messages
if [[ -n "$SESSION_JSONL" ]]; then
  uv run python -m memory conversation-logger backfill-codex-session \
    "$SESSION_JSONL" --interface codex
fi

# 6. Close conversation + backup
SESSION_ID=$(basename "$SESSION_JSONL" .jsonl | sed 's/.*-\([0-9a-f-]*\)$/\1/')
uv run python -m memory conversation-logger session-end-pi "$SESSION_ID" >/dev/null 2>&1
uv run python -m memory backup --silent >/dev/null 2>&1
```

This requires a new `backfill-codex-session` CLI command in the Python core to
parse Codex's JSONL format and log user/assistant turns.

---

## Implementation Plan (E6)

### S1 — `backfill-codex-session` CLI command
Parse `~/.codex/sessions/**/*.jsonl` and log user/assistant turns via the
existing `log-user` / `log-assistant` path. Same pattern as `backfill_pi_sessions`
but for Codex JSONL format.

### S2 — Wrapper script (`scripts/codex-mirror.sh`)
Session-start → `codex "$@"` → JSONL detection → backfill → session-end-pi + backup.

### S3 — `.agents/skills/mm-*/SKILL.md` symlinks
Same as Gemini CLI: symlink `.agents/skills/mm-*` → `.pi/skills/mm-*/`.
19 skills, zero maintenance.

### S4 — `AGENTS.md` in project root
Instructions for the model: Mirror Mind is active, use `/mm-mirror` for Mirror
Mode, `/mm-build` for Builder Mode, etc. Points the model to the skill surface.

### S5 — Smoke test + docs

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV8.E5.S1 | Inspect Codex capabilities | Done |
| CV8.E5.S2 | Map lifecycle to runtime contract | Done |
| CV8.E5.S3 | Decide target parity level (L3) | Done |
| CV8.E5.S4 | Draft implementation plan | Done |

---

## See also

- [CV8.E6 Codex Runtime Implementation](../cv8-e6-codex-runtime-implementation/index.md)
- [Codex implementation checklist](codex-checklist.md)
- [Runtime Interface Contract](../../../runtime-interface.md)
