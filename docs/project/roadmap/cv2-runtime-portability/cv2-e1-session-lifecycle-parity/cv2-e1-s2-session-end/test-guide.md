[< CV2.E1.S2 Plan](plan.md)

# CV2.E1.S2 — Test Guide: Align log-session-end.sh to unified CLI dispatch

## Scope

Shell script dispatch change only. No Python logic changes.
Tests cover:

1. `session-end` CLI command routes to `hook_session_end()` (existing coverage)
2. `backup --silent` CLI command works (existing coverage)
3. Hook script exits cleanly after the change

---

## Existing Tests to Run

```bash
pytest tests/ -k "session_end or hook_session_end or backup" -v
```

Must pass before and after the change.

---

## Manual Smoke Test

Simulate what Claude Code sends at session end (stdin JSON with empty session_id):

```bash
echo '{"session_id": "", "transcript_path": ""}' | bash .claude/hooks/log-session-end.sh
echo "exit code: $?"
```

Expected: exit code 0, no Python traceback in stderr.

Also verify each CLI command independently:

```bash
echo '{"session_id": "nonexistent", "transcript_path": ""}' | python3 -m memory conversation-logger session-end
python3 -m memory backup --silent
```

Both must exit 0.

---

## Full Verification Suite

```bash
pytest tests/ -x
ruff check src/ tests/
ruff format --check src/ tests/
pyright src/
git diff --check
```

All must pass clean.
