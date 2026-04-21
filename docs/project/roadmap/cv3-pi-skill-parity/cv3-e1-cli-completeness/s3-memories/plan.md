[< CV3.E1 CLI Completeness](../index.md)

# CV3.E1.S3 — Plan: Add `memories` CLI command

## Change

Create `src/memory/cli/memories.py` with a `main()` function.
Extract logic from `.claude/skills/mm:memories/run.py`.

The existing skill uses direct SQL for the list path. Preserve that for now —
refactoring to a MemoryClient method is a separate concern.

Wire in `src/memory/__main__.py`:
```python
elif command == "memories":
    from memory.cli.memories import main as _memories_main
    sys.argv = [sys.argv[0], *sys.argv[2:]]
    _memories_main()
```

## Interface

```
python -m memory memories [--type TYPE] [--layer LAYER] [--journey SLUG] [--limit N] [--search QUERY]
```

## No changes to
- `.claude/skills/mm:memories/run.py`
