[< CV2.E1 Session Lifecycle Parity](../index.md)

# CV2.E1.S1 — Plan: Align session-start.sh to unified CLI command

## What and Why

`session-start.sh` calls `python3 -m memory.cli.conversation_logger unmute`.
That is the old module-path invocation and only does one of the three things
the `session-start` CLI command does.

Pi's `session_start` handler calls `python -m memory conversation-logger session-start`,
which runs `session_start()`: unmute + close stale orphans + run pending extraction.

Result: orphan conversations and pending memory extraction only happen when Pi
starts, never when Claude Code starts.

Fix: one-line change to `session-start.sh`.

---

## Change

**File:** `.claude/hooks/session-start.sh`

**Before:**
```bash
python3 -m memory.cli.conversation_logger unmute 2>/dev/null || true
```

**After:**
```bash
python3 -m memory conversation-logger session-start 2>/dev/null || true
```

No Python code changes. No new CLI commands. The `session-start` subcommand
already exists in `conversation_logger.main()` at line 423.

---

## Verification

```bash
bash .claude/hooks/session-start.sh
```

Expected: prints a summary string (e.g. `"Memory ready."` or `"Closed 1 stale conversation(s). Extracted 2 memories."`) or empty string — no error exit code.

Also verify via the CLI directly:
```bash
python3 -m memory conversation-logger session-start
```
