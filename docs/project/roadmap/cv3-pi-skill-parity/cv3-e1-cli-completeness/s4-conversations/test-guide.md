[< S4 Plan](plan.md)

# CV3.E1.S4 — Test Guide: `conversations` CLI command

## Smoke tests
```bash
python -m memory conversations --limit 5
python -m memory conversations --journey mirror-poc --limit 3
```

## Full suite
```bash
pytest tests/ -x -q && ruff check src/ tests/ && ruff format --check src/ tests/ && pyright src/
```
