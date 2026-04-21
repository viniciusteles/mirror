"""Tests for journeys CLI behavior."""

from memory import MemoryClient
from memory.config import default_db_path_for_home

JOURNEY_CONTENT = """# Mirror POC
**Status:** active

## Description

Scoped journey description.
"""


def test_journeys_reads_from_explicit_mirror_home(tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "pati"
    db_path = default_db_path_for_home(mirror_home)
    mem = MemoryClient(env="test", db_path=db_path)
    mem.set_identity("journey", "mirror-poc", JOURNEY_CONTENT)

    from memory.cli.journeys import main

    main(["--mirror-home", str(mirror_home)])

    captured = capsys.readouterr()
    assert "mirror-poc" in captured.out
    assert "Scoped journey description." in captured.out


def test_journeys_explicit_mirror_home_overrides_environment_selection(mocker, tmp_path, capsys):
    env_home = tmp_path / ".mirror" / "vinicius"
    env_db_path = default_db_path_for_home(env_home)
    env_mem = MemoryClient(env="test", db_path=env_db_path)
    env_mem.set_identity("journey", "env-journey", JOURNEY_CONTENT.replace("Mirror POC", "Env"))

    explicit_home = tmp_path / ".mirror" / "pati"
    explicit_db_path = default_db_path_for_home(explicit_home)
    explicit_mem = MemoryClient(env="test", db_path=explicit_db_path)
    explicit_mem.set_identity("journey", "mirror-poc", JOURNEY_CONTENT)

    mocker.patch.dict("os.environ", {"MIRROR_HOME": str(env_home)}, clear=False)

    from memory.cli.journeys import main

    main(["--mirror-home", str(explicit_home)])

    captured = capsys.readouterr()
    assert "mirror-poc" in captured.out
    assert "env-journey" not in captured.out
