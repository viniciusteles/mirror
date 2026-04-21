[< CV2.E1 Session Lifecycle Parity](../index.md)

# CV2.E1.S2 — Plan: Align log-session-end.sh to unified CLI dispatch

## What and Why

`log-session-end.sh` uses inline Python to call `hook_session_end`:

```bash
python3 -c "from memory.cli.conversation_logger import hook_session_end; hook_session_end()" 2>/dev/null
python3 -m memory.cli.backup --silent 2>/dev/null
```

Both are old-style invocations:
- The inline `-c` import works but bypasses the CLI — it is fragile if the
  module path or function name changes.
- `memory.cli.backup` is the module path, not the CLI entrypoint.

The CLI already has proper commands for both:
- `python -m memory conversation-logger session-end` — calls `hook_session_end()`
- `python -m memory backup --silent` — runs backup

Fix: replace both lines with their CLI equivalents. Behavior is unchanged;
only the dispatch method changes.

---

## Change

**File:** `.claude/hooks/log-session-end.sh`

**Before:**
```bash
python3 -c "from memory.cli.conversation_logger import hook_session_end; hook_session_end()" 2>/dev/null
python3 -m memory.cli.backup --silent 2>/dev/null
```

**After:**
```bash
python3 -m memory conversation-logger session-end 2>/dev/null
python3 -m memory backup --silent 2>/dev/null
```

No Python code changes. Both CLI commands already exist.

---

## Note on session-end vs session-end-pi

`session-end` (Claude Code) calls `hook_session_end()`: reads JSON from stdin,
extracts immediately, backfills from transcript. This is correct for Claude Code
because Claude Code provides stdin JSON with `session_id` and `transcript_path`.

`session-end-pi` (Pi) calls `end_session(id, extract=False)`: no stdin, defers
extraction to next `session-start`. This is correct for Pi because Pi logs
messages explicitly and defers extraction.

The behaviors differ by design. This story does not change that — it only
fixes the dispatch style in the Claude Code hook.

---

## Verification

Confirm the CLI command exists and accepts stdin:

```bash
echo '{"session_id": "test-id", "transcript_path": ""}' | python3 -m memory conversation-logger session-end
```

Should exit 0 (may log a warning about unknown session, but must not crash).
