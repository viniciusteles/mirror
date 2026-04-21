[< CV3.E1 CLI Completeness](../index.md)

# CV3.E1.S8 — Plan: Add `save` CLI command

## Change

Create `src/memory/cli/save.py` with a `main()` function.
Extract logic from `.claude/skills/mm:save/run.py`.

Wire in `src/memory/__main__.py`:
```python
elif command == "save":
    from memory.cli.save import main as _save_main
    sys.argv = [sys.argv[0], *sys.argv[2:]]
    _save_main()
```

## Interface

```
python -m memory save [<slug>] [--full]
```

## Pi limitation

`mm:save` reads Claude Code JSONL transcript files from `~/.claude/projects/`.
Pi does not produce JSONL transcripts. On Pi, this command will fail gracefully
("transcript file not found") unless a transcript is available from a prior
Claude Code session. A DB-based export path is a future concern (CV4 or later).

The CLI command is added now so the Pi skill wrapper can exist; the Pi wrapper
will document the limitation.

## No changes to
- `.claude/skills/mm:save/run.py`
- `src/memory/cli/transcript_export.py`
