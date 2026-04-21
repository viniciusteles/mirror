[< CV3.E1 CLI Completeness](../index.md)

# CV3.E1.S2 — Plan: Add `journey` CLI command

## Change

Create `src/memory/cli/journey.py` with a `main()` function.
Extract logic from `.claude/skills/mm:journey/run.py` — uses `mem.get_journey_status()`
and `mem.set_journey_path()`, both proper MemoryClient methods.

Wire in `src/memory/__main__.py`:
```python
elif command == "journey":
    from memory.cli.journey import main as _journey_main
    sys.argv = [sys.argv[0], *sys.argv[2:]]
    _journey_main()
```

Note: `python -m memory mirror journeys` already handles `mm:journeys` (compact
list). The new `journey` command provides the full status view and path update.

## Interface

```
python -m memory journey [status [SLUG]]
python -m memory journey update <slug> <content>   # content='-' reads stdin
```

## No changes to
- `.claude/skills/mm:journey/run.py`
- `.claude/skills/mm:journeys/run.py`
