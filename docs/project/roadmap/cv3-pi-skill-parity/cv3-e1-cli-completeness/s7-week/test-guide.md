[< S7 Plan](plan.md)

# CV3.E1.S7 — Test Guide: `week` CLI command

## Smoke test (view only — no LLM)
```bash
python -m memory week
```
Expected: weekly view or "No items in the current week." Exit 0.

## Full suite
```bash
pytest tests/ -x -q && ruff check src/ tests/ && ruff format --check src/ tests/ && pyright src/
```
