[< CV3.E1 CLI Completeness](../index.md)

# CV3.E1.S4 — Plan: Add `conversations` CLI command

## Change

Create `src/memory/cli/conversations.py` with a `main()` function.
Extract logic from `.claude/skills/mm:conversations/run.py`.

Wire in `src/memory/__main__.py`:
```python
elif command == "conversations":
    from memory.cli.conversations import main as _conversations_main
    sys.argv = [sys.argv[0], *sys.argv[2:]]
    _conversations_main()
```

## Interface

```
python -m memory conversations [--limit N] [--journey SLUG] [--persona NAME]
```

## No changes to
- `.claude/skills/mm:conversations/run.py`
