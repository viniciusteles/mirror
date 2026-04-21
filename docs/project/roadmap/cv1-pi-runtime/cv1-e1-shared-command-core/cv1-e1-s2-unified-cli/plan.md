[< S2 Index](index.md)

# Plan — CV1.E1.S2

## Goal

Route `python -m memory mirror <subcommand>` and `python -m memory conversation-logger <subcommand>` through `src/memory/__main__.py`.

---

## Deliverables

### 1. `src/memory/skills/mirror.py` — gains `main(argv)`

```python
def main(argv: list[str] | None = None) -> None:
    """CLI entry point for `python -m memory mirror ...`"""
    import argparse, sys
    # argparse dispatch to load/deactivate/log/journeys
    # print output to stdout (same as run.py does today)
```

The display logic (banner, detection messages) belongs here for the unified CLI —
it mirrors what the Claude skill does. Pi can get its own display layer later.

### 2. `src/memory/cli/conversation_logger.py` — gains `main(argv)`

Extract the `if __name__ == "__main__"` block into a callable function:

```python
def main(argv: list[str] | None = None) -> None:
    """CLI entry point for `python -m memory conversation-logger ...`"""
    import sys
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        sys.exit(1)
    cmd = args[0]
    # existing dispatch logic, using args[1:] instead of sys.argv[2:]
```

The `if __name__ == "__main__"` block stays but calls `main()`.

### 3. `src/memory/__main__.py`

```python
elif command == "mirror":
    from memory.skills.mirror import main as _mirror_main
    _mirror_main(sys.argv[2:])

elif command == "conversation-logger":
    from memory.cli.conversation_logger import main as _logger_main
    _logger_main(sys.argv[2:])
```

Updated `USAGE` string documents all commands.

### 4. Tests

`tests/unit/memory/test_main.py` — new tests added alongside existing:

| Test | What it verifies |
|------|-----------------|
| `test_mirror_load_dispatches` | `mirror load --journey foo` calls `memory.skills.mirror.load` |
| `test_mirror_unknown_subcommand_exits` | Unknown subcommand exits nonzero |
| `test_conversation_logger_status_dispatches` | `conversation-logger status` calls `is_muted()` |
| `test_unknown_top_level_command_exits` | Unknown top-level command prints usage, exits 1 |

---

## Implementation Order

1. Add `main(argv)` to `src/memory/skills/mirror.py`
2. Extract `main(argv)` in `src/memory/cli/conversation_logger.py`
3. Update `src/memory/__main__.py` with two new routes + updated USAGE
4. Add tests to `tests/unit/memory/test_main.py`
5. Verify: `pytest tests/unit/memory/test_main.py`
