"""Tests for seeding identity YAML into the memory database."""

import json
from pathlib import Path
from textwrap import dedent

from memory.cli.seed import load_journey_content, load_persona_content, seed


def _write_yaml(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).lstrip(), encoding="utf-8")


def _write_core_identity(identity_root: Path) -> None:
    _write_yaml(
        identity_root / "self" / "soul.yaml",
        """
        soul: |
          Soul content.
        version: "1.0.0"
        """,
    )
    _write_yaml(
        identity_root / "ego" / "identity.yaml",
        """
        identity: |
          Ego identity content.
        version: "1.0.0"
        """,
    )
    _write_yaml(
        identity_root / "ego" / "behavior.yaml",
        """
        behavior: |
          Ego behavior content.
        version: "1.0.0"
        """,
    )
    _write_yaml(
        identity_root / "user" / "identity.yaml",
        """
        user: |
          User identity content.
        version: "1.0.0"
        """,
    )


def _write_journey(path: Path, *, key: str, value: str, name: str = "Mirror POC") -> None:
    _write_yaml(
        path,
        f"""
        {key}: {value}
        name: {name}
        status: active
        version: "1.0.0"
        description: >
          Test description.
        briefing: >
          Test briefing.
        context: |
          Test context.
        """,
    )


def test_load_journey_content_prefers_journey_id(tmp_path):
    journey_file = tmp_path / "mirror-poc.yaml"
    _write_journey(journey_file, key="journey_id", value="mirror-poc")

    journey_id, content, version = load_journey_content(journey_file)

    assert journey_id == "mirror-poc"
    assert "# Mirror POC" in content
    assert "Test description." in content
    assert version == "1.0.0"


def test_load_persona_content_preserves_routing_metadata(tmp_path):
    persona_file = tmp_path / "engineer.yaml"
    _write_yaml(
        persona_file,
        """
        persona_id: engineer
        name: Engineer
        version: "2.0.0"
        default_model: anthropic/claude-sonnet-4
        inherits_from: ego
        description: >
          Technical persona.
        system_prompt: |
          Engineer prompt.
        briefing: |
          Briefing text.
        routing_keywords:
        - python
        - debug
        - database
        """,
    )

    persona_id, content, version, metadata = load_persona_content(persona_file)

    assert persona_id == "engineer"
    assert "Engineer prompt." in content
    assert "# Briefing" in content
    assert version == "2.0.0"
    assert json.loads(metadata)["routing_keywords"] == ["python", "debug", "database"]


def test_load_journey_content_ignores_legacy_ids(tmp_path):
    journey_file = tmp_path / "mirror-poc.yaml"
    journey_file.write_text(
        """
travessia_id: other
name: Mirror POC
""".lstrip(),
        encoding="utf-8",
    )

    journey_id, _, _ = load_journey_content(journey_file)

    assert journey_id == "mirror-poc"


def test_seed_reads_from_user_home_identity_root(mocker, tmp_path, capsys):
    identity_root = tmp_path / ".mirror" / "testuser" / "identity"
    _write_core_identity(identity_root)
    _write_yaml(
        identity_root / "personas" / "engineer.yaml",
        """
        persona_id: engineer
        system_prompt: |
          Engineer prompt.
        routing_keywords:
        - python
        - debug
        version: "1.0.0"
        """,
    )
    _write_journey(
        identity_root / "journeys" / "mirror-poc.yaml", key="journey_id", value="mirror-poc"
    )

    client = mocker.Mock()
    client.store.get_identity.return_value = None
    memory_client = mocker.patch("memory.cli.seed.MemoryClient", return_value=client)

    result = seed(env="test", identity_root=identity_root)

    memory_client.assert_called_once_with(env="test")
    client.set_identity.assert_any_call("self", "soul", mocker.ANY, "1.0.0")
    client.set_identity.assert_any_call(
        "persona",
        "engineer",
        mocker.ANY,
        "1.0.0",
        json.dumps(
            {
                "persona_id": "engineer",
                "name": None,
                "inherits_from": None,
                "description": None,
                "routing_keywords": ["python", "debug"],
                "default_model": None,
            }
        ),
    )
    client.set_identity.assert_any_call("journey", "mirror-poc", mocker.ANY, "1.0.0")
    assert result["errors"] == []
    captured = capsys.readouterr()
    assert f"Mirror home: {identity_root.parent}" in captured.out


def test_seed_succeeds_when_optional_sections_are_absent(mocker, tmp_path):
    identity_root = tmp_path / "identity"
    _write_core_identity(identity_root)

    client = mocker.Mock()
    client.store.get_identity.return_value = None
    mocker.patch("memory.cli.seed.MemoryClient", return_value=client)

    result = seed(env="test", identity_root=identity_root)

    assert result["errors"] == []
    client.set_identity.assert_any_call("self", "soul", mocker.ANY, "1.0.0")
    assert not any(call.args[0] == "organization" for call in client.set_identity.call_args_list)


def test_seed_reports_missing_required_core_identity(mocker, tmp_path):
    identity_root = tmp_path / "identity"
    _write_yaml(
        identity_root / "ego" / "identity.yaml",
        """
        identity: |
          Ego identity content.
        version: "1.0.0"
        """,
    )
    _write_yaml(
        identity_root / "ego" / "behavior.yaml",
        """
        behavior: |
          Ego behavior content.
        version: "1.0.0"
        """,
    )
    _write_yaml(
        identity_root / "user" / "identity.yaml",
        """
        user: |
          User identity content.
        version: "1.0.0"
        """,
    )

    client = mocker.Mock()
    client.store.get_identity.return_value = None
    mocker.patch("memory.cli.seed.MemoryClient", return_value=client)

    result = seed(env="test", identity_root=identity_root)

    assert any(error.startswith("self/soul:") for error in result["errors"])


def test_seed_reads_from_explicit_mirror_home_identity_root(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "pati"
    identity_root = mirror_home / "identity"
    _write_core_identity(identity_root)
    _write_journey(
        identity_root / "journeys" / "mirror-poc.yaml", key="journey_id", value="mirror-poc"
    )

    client = mocker.Mock()
    client.store.get_identity.return_value = None
    memory_client = mocker.patch("memory.cli.seed.MemoryClient", return_value=client)

    result = seed(env="test", mirror_home=mirror_home)

    # When --mirror-home is explicit, the seed must write to that home's DB,
    # not to the env-default DB.
    memory_client.assert_called_once_with(db_path=mirror_home / "memory.db")
    client.set_identity.assert_any_call("journey", "mirror-poc", mocker.ANY, "1.0.0")
    assert result["errors"] == []
    captured = capsys.readouterr()
    assert f"Mirror home: {mirror_home}" in captured.out
    assert f"Identity root: {identity_root}" in captured.out


def test_seed_explicit_mirror_home_overrides_environment_selection(mocker, tmp_path):
    env_home = tmp_path / ".mirror" / "testuser"
    env_identity_root = env_home / "identity"
    _write_core_identity(env_identity_root)
    explicit_home = tmp_path / ".mirror" / "pati"
    explicit_identity_root = explicit_home / "identity"
    _write_core_identity(explicit_identity_root)
    _write_journey(
        explicit_identity_root / "journeys" / "mirror-poc.yaml",
        key="journey_id",
        value="mirror-poc",
    )

    client = mocker.Mock()
    client.store.get_identity.return_value = None
    memory_client = mocker.patch("memory.cli.seed.MemoryClient", return_value=client)
    mocker.patch.dict("os.environ", {"MIRROR_HOME": str(env_home)}, clear=False)

    result = seed(env="test", mirror_home=explicit_home)

    assert result["errors"] == []
    # The explicit mirror_home must win over the MIRROR_HOME env var both for
    # reading identity files and for resolving the database path.
    memory_client.assert_called_once_with(db_path=explicit_home / "memory.db")
    client.set_identity.assert_any_call("journey", "mirror-poc", mocker.ANY, "1.0.0")


def test_seed_does_not_fall_back_to_repo_identity(mocker, tmp_path):
    identity_root = tmp_path / "missing-identity"
    client = mocker.Mock()
    client.store.get_identity.return_value = None
    mocker.patch("memory.cli.seed.MemoryClient", return_value=client)

    result = seed(env="test", identity_root=identity_root)

    assert any(error.startswith("self/soul:") for error in result["errors"])
    assert client.set_identity.call_args_list == []


def test_seed_writes_to_explicit_mirror_home_database(tmp_path):
    """Regression test: --mirror-home must drive both reads (identity files)
    and writes (database path). Without this guarantee, seeding a demo or
    secondary user home would silently pollute the env-default user's DB.
    """
    from memory.client import MemoryClient

    explicit_home = tmp_path / ".mirror-demo" / "persona-x"
    identity_root = explicit_home / "identity"
    _write_core_identity(identity_root)
    _write_journey(
        identity_root / "journeys" / "mirror-poc.yaml",
        key="journey_id",
        value="mirror-poc",
    )

    other_home = tmp_path / ".mirror" / "other-user"
    other_home.mkdir(parents=True)
    other_db = other_home / "memory.db"

    result = seed(env="test", mirror_home=explicit_home)

    assert result["errors"] == []
    expected_db = explicit_home / "memory.db"
    assert expected_db.exists(), "seed must create DB inside the explicit mirror_home"
    assert not other_db.exists(), (
        "seed must not write to any other home when --mirror-home is explicit"
    )

    client = MemoryClient(db_path=expected_db)
    try:
        assert client.store.get_identity("journey", "mirror-poc") is not None
        assert client.store.get_identity("self", "soul") is not None
    finally:
        client.close()
