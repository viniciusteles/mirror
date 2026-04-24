"""Tests for inspect CLI mirror-home selection."""

import json

from memory import MemoryClient
from memory.cli.inspect import cmd_detect_persona, cmd_inspect, cmd_list
from memory.config import default_db_path_for_home

PERSONA_CONTENT = """# Writer

Persona content.
"""
JOURNEY_CONTENT = """# Mirror POC
**Status:** active

## Description

Scoped journey description.
"""


def test_list_reads_from_explicit_mirror_home(tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "pati"
    db_path = default_db_path_for_home(mirror_home)
    mem = MemoryClient(env="test", db_path=db_path)
    mem.set_identity("persona", "writer", PERSONA_CONTENT)
    mem.set_identity("journey", "mirror-poc", JOURNEY_CONTENT)

    cmd_list(["all", "--mirror-home", str(mirror_home)])

    output = capsys.readouterr().out
    assert "writer" in output
    assert "mirror-poc" in output


def test_list_explicit_mirror_home_overrides_environment_selection(mocker, tmp_path, capsys):
    env_home = tmp_path / ".mirror" / "testuser"
    explicit_home = tmp_path / ".mirror" / "pati"

    env_mem = MemoryClient(env="test", db_path=default_db_path_for_home(env_home))
    env_mem.set_identity("persona", "env-persona", PERSONA_CONTENT)

    explicit_mem = MemoryClient(env="test", db_path=default_db_path_for_home(explicit_home))
    explicit_mem.set_identity("persona", "writer", PERSONA_CONTENT)

    mocker.patch.dict("os.environ", {"MIRROR_HOME": str(env_home)}, clear=False)

    cmd_list(["personas", "--mirror-home", str(explicit_home)])

    output = capsys.readouterr().out
    assert "writer" in output
    assert "env-persona" not in output


def test_inspect_reads_from_explicit_mirror_home(tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "pati"
    db_path = default_db_path_for_home(mirror_home)
    mem = MemoryClient(env="test", db_path=db_path)
    mem.set_identity(
        "persona",
        "writer",
        PERSONA_CONTENT,
        metadata=json.dumps({"routing_keywords": ["article", "draft"]}),
    )

    cmd_inspect(["persona", "writer", "--mirror-home", str(mirror_home)])

    output = capsys.readouterr().out
    assert "=== persona/writer ===" in output
    assert "routing_keywords: article, draft" in output


def test_detect_persona_reads_from_explicit_mirror_home(tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "pati"
    db_path = default_db_path_for_home(mirror_home)
    mem = MemoryClient(env="test", db_path=db_path)
    mem.set_identity(
        "persona",
        "engineer",
        "Engineer prompt.",
        metadata=json.dumps({"routing_keywords": ["python", "debug"]}),
    )

    cmd_detect_persona(["debug", "this", "python", "issue", "--mirror-home", str(mirror_home)])

    output = capsys.readouterr().out
    assert "engineer: 2.0 (keyword)" in output


def test_inspect_extension_reads_from_explicit_mirror_home(tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "pati"
    ext_dir = mirror_home / "extensions" / "review-copy"
    ext_dir.mkdir(parents=True)
    (ext_dir / "SKILL.md").write_text("# Review Copy\n", encoding="utf-8")
    (ext_dir / "skill.yaml").write_text(
        "\n".join(
            [
                "id: review-copy",
                "name: Review Copy",
                "category: extension",
                "kind: prompt-skill",
                "summary: Multi-LLM copy review workflow",
                "runtimes:",
                "  pi:",
                "    command_name: ext-review-copy",
                "    skill_file: SKILL.md",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    cmd_inspect(["extension", "review-copy", "--mirror-home", str(mirror_home)])

    output = capsys.readouterr().out
    assert "=== extension/review-copy ===" in output
    assert "command_name: ext-review-copy" in output
    assert f"root: {ext_dir}" in output
