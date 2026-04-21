[< S3 Plan](plan.md)

# CV3.E1.S3 — Test Guide: `memories` CLI command

## Smoke tests
```bash
python -m memory memories --limit 5
python -m memory memories --journey mirror-poc --limit 3
python -m memory memories --search "session lifecycle" --limit 5
```

## Full suite
```bash
pytest tests/ -x -q && ruff check src/ tests/ && ruff format --check src/ tests/ && pyright src/
```
