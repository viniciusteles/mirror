[< S2 Plan](plan.md)

# CV3.E1.S2 — Test Guide: `journey` CLI command

## Smoke tests
```bash
python -m memory journey status mirror
python -m memory journey update mirror "New path content"
echo "Stdin content" | python -m memory journey update mirror -
```

## Full suite
```bash
pytest tests/ -x -q && ruff check src/ tests/ && ruff format --check src/ tests/ && pyright src/
```
