"""Tests for task management CLI behavior."""

from memory import MemoryClient
from memory.config import default_db_path_for_home


def test_tasks_list_reads_from_explicit_mirror_home(tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "pati"
    db_path = default_db_path_for_home(mirror_home)
    mem = MemoryClient(env="test", db_path=db_path)
    mem.add_task(title="Scoped task", journey="mirror-poc")

    from memory.cli.tasks_cmd import main

    main(["--mirror-home", str(mirror_home), "list"])

    captured = capsys.readouterr()
    assert "Scoped task" in captured.out
    assert "mirror-poc" in captured.out


def test_tasks_add_explicit_mirror_home_overrides_environment_selection(mocker, tmp_path, capsys):
    env_home = tmp_path / ".mirror" / "testuser"
    explicit_home = tmp_path / ".mirror" / "pati"
    mocker.patch.dict("os.environ", {"MIRROR_HOME": str(env_home)}, clear=False)

    from memory.cli.tasks_cmd import main

    main(["--mirror-home", str(explicit_home), "add", "Explicit task", "--journey", "mirror-poc"])

    captured = capsys.readouterr()
    assert "Task created" in captured.out

    env_mem = MemoryClient(env="test", db_path=default_db_path_for_home(env_home))
    explicit_mem = MemoryClient(env="test", db_path=default_db_path_for_home(explicit_home))
    assert env_mem.list_tasks() == []
    explicit_tasks = explicit_mem.list_tasks()
    assert len(explicit_tasks) == 1
    assert explicit_tasks[0].title == "Explicit task"
