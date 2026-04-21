[< Plan](plan.md)

# CV5.E1.S2 — Test Guide — Session-Scoped Mirror State and Routing

## Automated

- `pytest tests/unit/memory/hooks/test_mirror_state.py`
- `pytest tests/unit/memory/skills/test_mirror.py`
- `pytest tests/unit/memory/cli/test_conversation_logger.py -k "switch or current or mirror"`

## Targeted Assertions

- session A and session B can both be mirror-active with different persona/journey
- marking hook injection for one session does not affect the other
- switching the conversation for one session leaves the other session untouched
- logging an assistant summary for one session goes to that session's conversation
