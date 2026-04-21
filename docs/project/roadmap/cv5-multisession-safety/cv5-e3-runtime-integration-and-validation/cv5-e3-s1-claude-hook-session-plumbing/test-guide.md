[< Plan](plan.md)

# CV5.E3.S1 — Test Guide — Claude Hook Session Plumbing

## Automated

- `pytest tests/unit/memory/hooks/test_current_session.py`
- `pytest tests/unit/memory/hooks/test_mirror_state.py`
- `pytest tests/unit/memory/skills/test_mirror.py`

## Targeted Assertions

- hook scripts and helpers can resolve session ids directly from hook payloads
- mirror reinjection checks are isolated per session
- explicit `/mm:mirror` activation does not overwrite another active session's state
