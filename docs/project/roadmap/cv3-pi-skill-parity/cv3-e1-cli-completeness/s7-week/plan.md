[< CV3.E1 CLI Completeness](../index.md)

# CV3.E1.S7 — Plan: Add `week` CLI command

## Change

Create `src/memory/cli/week.py` with a `main()` function.
Extract logic from `.claude/skills/mm:week/run.py`.

Wire in `src/memory/__main__.py`:
```python
elif command == "week":
    from memory.cli.week import main as _week_main
    sys.argv = [sys.argv[0], *sys.argv[2:]]
    _week_main()
```

## Interface

```
python -m memory week              # show current week (default)
python -m memory week --ingest     # read free text from stdin and schedule items
```

## Note on LLM dependency

The `--ingest` path calls an LLM (OpenRouter) to parse free-text plans into
structured tasks. This is the same dependency `mm:consult` has. It works on
any runtime that has `OPENROUTER_API_KEY` set — no special handling needed.

## No changes to
- `.claude/skills/mm:week/run.py`
