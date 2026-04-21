[< CV3.E1 CLI Completeness](../index.md)

# CV3.E1.S5 — Plan: Add `recall` CLI command

## Change

Create `src/memory/cli/recall.py` with a `main()` function.
Extract logic from `.claude/skills/mm:recall/run.py`.

Wire in `src/memory/__main__.py`:
```python
elif command == "recall":
    from memory.cli.recall import main as _recall_main
    sys.argv = [sys.argv[0], *sys.argv[2:]]
    _recall_main()
```

## Interface

```
python -m memory recall <conversation_id_prefix> [--limit N]
```

## No changes to
- `.claude/skills/mm:recall/run.py`
