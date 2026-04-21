[< Plan](plan.md)

# CV5.E2.S1 — Test Guide — Eliminate File-Based Session Races

## Automated

- `pytest tests/unit/memory/cli/test_conversation_logger.py`
- targeted concurrency regression test for session creation

## Targeted Assertions

- no lost updates under concurrent `get_or_create_conversation` calls
- imported Pi sessions are deduplicated by DB-backed session registry
- end-session removes active routing without deleting historical session binding
