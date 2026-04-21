[< S8 Plan](plan.md)

# CV3.E1.S8 — Test Guide: `save` CLI command

## Smoke test (Claude Code session active)
```bash
python -m memory save my-export
```
Expected: prints file path to exported Markdown, exit 0.

## Graceful failure (no transcript)
```bash
CURRENT_SESSION_PATH=/nonexistent python -m memory save
```
Expected: "transcript file not found", exit 1.

## Full suite
```bash
pytest tests/ -x -q && ruff check src/ tests/ && ruff format --check src/ tests/ && pyright src/
```
