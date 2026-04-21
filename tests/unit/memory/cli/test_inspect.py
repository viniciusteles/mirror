"""Tests for memory inspection CLI helpers."""

import json
from pathlib import Path

import pytest

from memory.cli.inspect import cmd_detect_persona, cmd_inspect, cmd_list
from memory.models import Identity

PROJECT_ROOT = Path(__file__).resolve().parents[4]


def test_list_journeys_reads_english_identity_layer(mocker, capsys):
    client = mocker.Mock()
    client.get_identity.return_value = [
        Identity(layer="journey", key="mirror-poc", content="# Mirror POC\n**Status:** active")
    ]
    mocker.patch("memory.client.MemoryClient", return_value=client)

    cmd_list(["journeys"])

    output = capsys.readouterr().out
    client.get_identity.assert_called_once_with(layer="journey")
    assert "=== JOURNEYS ===" in output
    assert "[active] mirror-poc" in output


def test_list_journeys_does_not_fall_back_to_legacy_layer(mocker, capsys):
    client = mocker.Mock()
    client.get_identity.return_value = []
    mocker.patch("memory.client.MemoryClient", return_value=client)

    cmd_list(["journeys"])

    output = capsys.readouterr().out
    client.get_identity.assert_called_once_with(layer="journey")
    assert "  (none)" in output


def test_list_personas_verbose_shows_routing_keywords(mocker, capsys):
    client = mocker.Mock()
    client.get_identity.return_value = [
        Identity(
            layer="persona",
            key="writer",
            content="Writer prompt.",
            metadata=json.dumps({"routing_keywords": ["article", "draft"]}),
        )
    ]
    mocker.patch("memory.client.MemoryClient", return_value=client)

    cmd_list(["personas", "--verbose"])

    output = capsys.readouterr().out
    assert "writer" in output
    assert "routing_keywords: article, draft" in output


def test_list_extensions_reads_from_explicit_extensions_root(capsys):
    cmd_list(["extensions", "--extensions-root", str(PROJECT_ROOT / "examples" / "extensions")])

    output = capsys.readouterr().out
    assert "=== EXTENSIONS ===" in output
    assert "review-copy [prompt-skill]" in output


def test_list_extensions_filters_by_runtime(capsys):
    cmd_list(
        [
            "extensions",
            "--extensions-root",
            str(PROJECT_ROOT / "examples" / "extensions"),
            "--runtime",
            "pi",
        ]
    )

    output = capsys.readouterr().out
    assert "Runtime filter: pi" in output
    assert "review-copy [prompt-skill]" in output


def test_inspect_persona_shows_metadata_and_content(mocker, capsys):
    client = mocker.Mock()
    client.store.get_identity.return_value = Identity(
        layer="persona",
        key="writer",
        content="Writer prompt.",
        version="2.0.0",
        metadata=json.dumps(
            {
                "persona_id": "writer",
                "name": "Writer",
                "routing_keywords": ["article", "draft"],
            }
        ),
    )
    mocker.patch("memory.client.MemoryClient", return_value=client)

    cmd_inspect(["persona", "writer"])

    output = capsys.readouterr().out
    assert "=== persona/writer ===" in output
    assert "routing_keywords: article, draft" in output
    assert "Writer prompt." in output


def test_inspect_persona_exits_when_missing(mocker):
    client = mocker.Mock()
    client.store.get_identity.return_value = None
    mocker.patch("memory.client.MemoryClient", return_value=client)

    with pytest.raises(SystemExit):
        cmd_inspect(["persona", "missing"])


def test_detect_persona_prints_ranked_matches(mocker, capsys):
    client = mocker.Mock()
    client.detect_persona.return_value = [("engineer", 3.0, "keyword")]
    mocker.patch("memory.client.MemoryClient", return_value=client)

    cmd_detect_persona(["debug", "this", "python", "issue"])

    output = capsys.readouterr().out
    assert "query: debug this python issue" in output
    assert "engineer: 3.0 (keyword)" in output


def test_inspect_extension_shows_manifest_details(capsys):
    cmd_inspect(
        [
            "extension",
            "review-copy",
            "--extensions-root",
            str(PROJECT_ROOT / "examples" / "extensions"),
        ]
    )

    output = capsys.readouterr().out
    assert "=== extension/review-copy ===" in output
    assert "kind: prompt-skill" in output
    assert "command_name: ext:review-copy" in output
    assert "command_name: ext-review-copy" in output
    assert "skill_file: SKILL.md" in output


def test_inspect_extension_exits_when_missing(tmp_path):
    with pytest.raises(SystemExit):
        cmd_inspect(["extension", "missing", "--extensions-root", str(tmp_path)])


def test_inspect_runtime_catalog_shows_catalog_details(tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "pati"
    runtime_root = mirror_home / "runtime" / "skills" / "pi"
    runtime_root.mkdir(parents=True, exist_ok=True)
    (runtime_root / "extensions.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "runtime": "pi",
                "target_root": str(runtime_root),
                "generated_at": "2026-04-21T18:00:00+00:00",
                "extensions": [
                    {
                        "id": "review-copy",
                        "command_name": "ext-review-copy",
                        "kind": "prompt-skill",
                        "installed_skill_path": str(runtime_root / "ext-review-copy" / "SKILL.md"),
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    cmd_inspect(["runtime-catalog", "pi", "--mirror-home", str(mirror_home)])

    output = capsys.readouterr().out
    assert "=== runtime-catalog/pi ===" in output
    assert "schema_version: 1" in output
    assert "review-copy -> ext-review-copy" in output
