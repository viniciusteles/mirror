"""Tests for Builder Mode CLI context loader."""

from memory import MemoryClient
from memory.cli import build
from memory.config import default_db_path_for_home

JOURNEY_CONTENT = """# Mirror POC
**Status:** active

## Description

Scoped journey description.
"""


def test_build_load_reads_project_path_from_journey_service(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "pati"
    db_path = default_db_path_for_home(mirror_home)
    mem = MemoryClient(env="test", db_path=db_path)
    mem.set_identity("journey", "mirror-poc", JOURNEY_CONTENT)
    project_path = tmp_path / "project"
    mem.journeys.set_project_path("mirror-poc", str(project_path))

    mocker.patch("memory.cli.build.MemoryClient", return_value=mem)
    mocker.patch("memory.cli.build.switch_conversation")
    mocker.patch("memory.cli.build._persist_global_sticky_defaults")
    mocker.patch.object(mem, "load_mirror_context", return_value="context")
    mocker.patch.object(mem, "search", return_value=[])

    build.cmd_load("mirror-poc")

    captured = capsys.readouterr()
    assert f"project_path={project_path.resolve()}" in captured.out
