"""Tests for week CLI behavior."""

import json
from datetime import date

from memory import MemoryClient
from memory.config import default_db_path_for_home


def test_week_view_reads_from_explicit_mirror_home(tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "pati"
    db_path = default_db_path_for_home(mirror_home)
    mem = MemoryClient(env="test", db_path=db_path)
    mem.add_task(title="Scoped week task", due_date=date.today().isoformat(), journey="mirror-poc")

    from memory.cli.week import main

    main(["--mirror-home", str(mirror_home), "view"])

    captured = capsys.readouterr()
    assert "Scoped week task" in captured.out
    assert "mirror-poc" in captured.out


def test_week_save_explicit_mirror_home_overrides_environment_selection(mocker, tmp_path, capsys):
    pending_file = tmp_path / "pending.json"
    pending_file.write_text(
        json.dumps(
            [
                {
                    "title": "Explicit week item",
                    "due_date": date.today().isoformat(),
                    "scheduled_at": None,
                    "time_hint": None,
                    "journey": "mirror-poc",
                    "context": None,
                }
            ]
        ),
        encoding="utf-8",
    )
    mocker.patch("memory.cli.week.PENDING_FILE", pending_file)

    env_home = tmp_path / ".mirror" / "testuser"
    explicit_home = tmp_path / ".mirror" / "pati"
    mocker.patch.dict("os.environ", {"MIRROR_HOME": str(env_home)}, clear=False)

    from memory.cli.week import main

    main(["--mirror-home", str(explicit_home), "save"])

    captured = capsys.readouterr()
    assert "1 items saved" in captured.out

    env_mem = MemoryClient(env="test", db_path=default_db_path_for_home(env_home))
    explicit_mem = MemoryClient(env="test", db_path=default_db_path_for_home(explicit_home))
    assert env_mem.list_tasks() == []
    explicit_tasks = explicit_mem.list_tasks()
    assert len(explicit_tasks) == 1
    assert explicit_tasks[0].title == "Explicit week item"
