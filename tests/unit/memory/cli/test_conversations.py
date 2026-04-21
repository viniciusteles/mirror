"""Tests for conversations CLI behavior."""

from memory import MemoryClient
from memory.config import default_db_path_for_home


def test_conversations_reads_from_explicit_mirror_home(tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "pati"
    db_path = default_db_path_for_home(mirror_home)
    mem = MemoryClient(env="test", db_path=db_path)
    conv = mem.start_conversation(
        "cli", persona="engineer", journey="mirror-poc", title="Scoped conversation"
    )
    mem.add_message(conv.id, "user", "Hello")

    from memory.cli.conversations import main

    main(["--mirror-home", str(mirror_home)])

    captured = capsys.readouterr()
    assert "Scoped conversation" in captured.out
    assert "mirror-poc" in captured.out
    assert conv.id[:8] in captured.out


def test_conversations_explicit_mirror_home_overrides_environment_selection(
    mocker, tmp_path, capsys
):
    env_home = tmp_path / ".mirror" / "vinicius"
    env_db_path = default_db_path_for_home(env_home)
    env_mem = MemoryClient(env="test", db_path=env_db_path)
    env_conv = env_mem.start_conversation("cli", title="Environment conversation")
    env_mem.add_message(env_conv.id, "user", "env")

    explicit_home = tmp_path / ".mirror" / "pati"
    explicit_db_path = default_db_path_for_home(explicit_home)
    explicit_mem = MemoryClient(env="test", db_path=explicit_db_path)
    explicit_conv = explicit_mem.start_conversation("cli", title="Explicit conversation")
    explicit_mem.add_message(explicit_conv.id, "user", "explicit")

    mocker.patch.dict("os.environ", {"MIRROR_HOME": str(env_home)}, clear=False)

    from memory.cli.conversations import main

    main(["--mirror-home", str(explicit_home)])

    captured = capsys.readouterr()
    assert "Explicit conversation" in captured.out
    assert "Environment conversation" not in captured.out
