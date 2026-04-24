"""Tests for journey CLI behavior."""

from memory import MemoryClient
from memory.config import default_db_path_for_home

JOURNEY_CONTENT = """# Mirror POC
**Status:** active

## Description

Scoped journey description.
"""


def test_journey_status_reads_from_explicit_mirror_home(tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "pati"
    db_path = default_db_path_for_home(mirror_home)
    mem = MemoryClient(env="test", db_path=db_path)
    mem.set_identity("journey", "mirror-poc", JOURNEY_CONTENT)
    mem.set_journey_path("mirror-poc", "# Journey path")
    mem.add_message(
        mem.start_conversation("cli", journey="mirror-poc", title="Scoped conversation").id,
        "user",
        "hello",
    )

    from memory.cli.journey import main

    main(["status", "mirror-poc", "--mirror-home", str(mirror_home)])

    captured = capsys.readouterr()
    assert "=== journey: mirror-poc ===" in captured.out
    assert "Scoped journey description." in captured.out
    assert "Scoped conversation" in captured.out


def test_journey_update_explicit_mirror_home_overrides_environment_selection(
    mocker, tmp_path, capsys
):
    env_home = tmp_path / ".mirror" / "testuser"
    env_db_path = default_db_path_for_home(env_home)
    env_mem = MemoryClient(env="test", db_path=env_db_path)
    env_mem.set_identity("journey", "mirror-poc", JOURNEY_CONTENT)

    explicit_home = tmp_path / ".mirror" / "pati"
    explicit_db_path = default_db_path_for_home(explicit_home)
    explicit_mem = MemoryClient(env="test", db_path=explicit_db_path)
    explicit_mem.set_identity("journey", "mirror-poc", JOURNEY_CONTENT)

    mocker.patch.dict("os.environ", {"MIRROR_HOME": str(env_home)}, clear=False)

    from memory.cli.journey import main

    main(["update", "mirror-poc", "# Explicit path", "--mirror-home", str(explicit_home)])

    captured = capsys.readouterr()
    assert "updated" in captured.err
    assert explicit_mem.get_journey_path("mirror-poc") == "# Explicit path"
    assert env_mem.get_journey_path("mirror-poc") is None
