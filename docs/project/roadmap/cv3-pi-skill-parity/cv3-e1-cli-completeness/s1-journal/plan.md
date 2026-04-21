[< CV3.E1 CLI Completeness](../index.md)

# CV3.E1.S1 — Plan: Add `journal` CLI command

## Change

Create `src/memory/cli/journal.py` with a `main()` function.
Extract logic from `.claude/skills/mm:journal/run.py` verbatim — it is clean
and uses `mem.add_journal()` through the proper MemoryClient interface.

Wire in `src/memory/__main__.py`:
```python
elif command == "journal":
    from memory.cli.journal import main as _journal_main
    sys.argv = [sys.argv[0], *sys.argv[2:]]
    _journal_main()
```

Update USAGE string to list the new command.

## Interface

```
python -m memory journal <text> [--journey SLUG]
```

## No changes to
- `.claude/skills/mm:journal/run.py` — stays as-is
- Any existing CLI commands
