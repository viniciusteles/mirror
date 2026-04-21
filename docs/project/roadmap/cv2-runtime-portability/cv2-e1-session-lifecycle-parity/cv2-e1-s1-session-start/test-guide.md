[< CV2.E1.S1 Plan](plan.md)

# CV2.E1.S1 — Test Guide: Align session-start.sh to unified CLI command

## Scope

The change is a one-line shell script edit. No Python logic changes.
Tests cover:

1. The `session-start` CLI command already behaves correctly (existing coverage)
2. The hook script calls the right command and exits cleanly

---

## Existing Tests to Run

```bash
pytest tests/ -k "session_start or orphan or extract_pending" -v
```

These should pass before and after the change. If they do not pass before,
the change is blocked — investigate first.

---

## Manual Smoke Test

Run the hook directly and confirm it exits 0 with no tracebacks:

```bash
bash .claude/hooks/session-start.sh
echo "exit code: $?"
```

Also run the CLI command standalone:

```bash
python3 -m memory conversation-logger session-start
```

Confirm output is a string (possibly empty) and exit code is 0.

---

## New Test (if coverage is missing)

If no test covers `session_start()` calling `close_stale_orphans` and
`extract_pending`, add one in `tests/test_conversation_logger.py`:

```python
def test_session_start_calls_all_three(monkeypatch):
    calls = []
    monkeypatch.setattr("memory.cli.conversation_logger.set_mute", lambda on: calls.append("unmute"))
    monkeypatch.setattr("memory.cli.conversation_logger.close_stale_orphans", lambda **kw: (calls.append("orphans"), 0)[1])
    monkeypatch.setattr("memory.cli.conversation_logger.extract_pending", lambda: (calls.append("extract"), 0)[1])
    session_start()
    assert "unmute" in calls
    assert "orphans" in calls
    assert "extract" in calls
```

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
