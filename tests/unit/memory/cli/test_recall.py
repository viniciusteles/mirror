"""Tests for recall CLI behavior."""

import pytest

from memory import MemoryClient
from memory.config import default_db_path_for_home


def test_recall_reads_from_explicit_mirror_home(tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "pati"
    db_path = default_db_path_for_home(mirror_home)
    mem = MemoryClient(env="test", db_path=db_path)
    conv = mem.start_conversation(
        "cli", persona="engineer", journey="mirror-poc", title="Scoped recall"
    )
    mem.add_message(conv.id, "user", "first message")
    mem.add_message(conv.id, "assistant", "second message")

    from memory.cli.recall import main

    main([conv.id[:8], "--mirror-home", str(mirror_home)])

    captured = capsys.readouterr()
    assert "Scoped recall" in captured.out
    assert "first message" in captured.out
    assert "second message" in captured.out
    assert "mirror-poc" in captured.out


def test_recall_explicit_mirror_home_overrides_environment_selection(mocker, tmp_path, capsys):
    env_home = tmp_path / ".mirror" / "testuser"
    env_db_path = default_db_path_for_home(env_home)
    env_mem = MemoryClient(env="test", db_path=env_db_path)
    env_conv = env_mem.start_conversation("cli", title="Environment recall")
    env_mem.add_message(env_conv.id, "user", "env")

    explicit_home = tmp_path / ".mirror" / "pati"
    explicit_db_path = default_db_path_for_home(explicit_home)
    explicit_mem = MemoryClient(env="test", db_path=explicit_db_path)
    explicit_conv = explicit_mem.start_conversation("cli", title="Explicit recall")
    explicit_mem.add_message(explicit_conv.id, "user", "explicit")

    mocker.patch.dict("os.environ", {"MIRROR_HOME": str(env_home)}, clear=False)

    from memory.cli.recall import main

    main([explicit_conv.id[:8], "--mirror-home", str(explicit_home)])

    captured = capsys.readouterr()
    assert "Explicit recall" in captured.out
    assert "explicit" in captured.out
    assert "Environment recall" not in captured.out


def test_recall_exits_when_conversation_is_missing_in_explicit_mirror_home(tmp_path):
    mirror_home = tmp_path / ".mirror" / "pati"
    db_path = default_db_path_for_home(mirror_home)
    MemoryClient(env="test", db_path=db_path)

    from memory.cli.recall import main

    with pytest.raises(SystemExit) as excinfo:
        main(["missing", "--mirror-home", str(mirror_home)])

    assert excinfo.value.code == 1
