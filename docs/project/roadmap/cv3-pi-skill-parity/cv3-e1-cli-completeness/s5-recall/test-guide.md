[< S5 Plan](plan.md)

# CV3.E1.S5 — Test Guide: `recall` CLI command

## Smoke test
```bash
# Get a real conversation ID prefix first
python -m memory conversations --limit 1
# Then recall it
python -m memory recall <prefix> --limit 10
```

## Error case
```bash
python -m memory recall nonexistent-id
```
Expected: error message, exit 1.

## Full suite
```bash
pytest tests/ -x -q && ruff check src/ tests/ && ruff format --check src/ tests/ && pyright src/
```
