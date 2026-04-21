[< CV3.E1 CLI Completeness](../index.md)

# CV3.E1.S6 — Plan: Wire `tasks` CLI command

## Change

`src/memory/cli/tasks.py` exists but only contains parsing utilities
(`parse_journey_path_tasks`, `parse_done_tasks`). The full task management
logic lives in `.claude/skills/mm:tasks/run.py`.

Create `src/memory/cli/tasks_cmd.py` with a `main()` function extracted from
the skill's run.py. (Cannot name it `tasks.py` — that file already exists with
the parsing utilities.)

Wire in `src/memory/__main__.py`:
```python
elif command == "tasks":
    from memory.cli.tasks_cmd import main as _tasks_main
    sys.argv = [sys.argv[0], *sys.argv[2:]]
    _tasks_main()
```

## Interface

```
python -m memory tasks [--journey SLUG] [--all] [--status STATUS]
python -m memory tasks add <title> [--journey SLUG] [--due DATE] [--stage STAGE]
python -m memory tasks update <id> --status STATUS
python -m memory tasks sync [--journey SLUG]   # sync from journey_path checkboxes
```

## No changes to
- `src/memory/cli/tasks.py` (parsing utilities — untouched)
- `.claude/skills/mm:tasks/run.py`
