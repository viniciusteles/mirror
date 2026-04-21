[< Plan](plan.md)

# CV5.E1.S1 — Test Guide — Runtime Session Registry

## Automated

- `pytest tests/unit/memory/storage/test_store.py -k runtime_session`
- `pytest tests/unit/memory/cli/test_conversation_logger.py`
- `pytest tests/unit/memory/skills/test_mirror.py`

## Targeted Assertions

- a session id can be bound to a conversation and read back
- mirror state fields persist independently per session
- a second session does not overwrite the first session's mapping
- concurrent creation of many sessions preserves all bindings
