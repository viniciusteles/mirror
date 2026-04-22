[< S6 Plan](plan.md)

# CV3.E1.S6 — Test Guide: `tasks` CLI command

## Smoke tests
```bash
python -m memory tasks --journey mirror
python -m memory tasks add "Test task" --journey mirror
python -m memory tasks --all --journey mirror
```

## Full suite
```bash
pytest tests/ -x -q && ruff check src/ tests/ && ruff format --check src/ tests/ && pyright src/
```
