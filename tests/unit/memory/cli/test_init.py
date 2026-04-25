"""Tests for bootstrapping a user home from repository templates."""

from pathlib import Path

from memory.cli.init import find_templates_identity_root, init_user_home


def _write_template(path: Path, content: str = "template") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_init_user_home_copies_templates_into_identity_root(tmp_path):
    templates_root = tmp_path / "templates" / "identity"
    _write_template(templates_root / "self" / "config.yaml", "config: value\n")
    _write_template(templates_root / "personas" / "writer.yaml", "persona_id: writer\n")

    destination_root = tmp_path / ".mirror" / "testuser"

    created_identity_root = init_user_home(
        "testuser", templates_identity_root=templates_root, user_home=destination_root
    )

    assert created_identity_root == destination_root / "identity"
    assert (created_identity_root / "self" / "config.yaml").read_text(
        encoding="utf-8"
    ) == "config: value\n"
    assert (created_identity_root / "personas" / "writer.yaml").read_text(
        encoding="utf-8"
    ) == "persona_id: writer\n"


def test_init_user_home_creates_parent_directories(tmp_path):
    templates_root = tmp_path / "templates" / "identity"
    _write_template(templates_root / "self" / "config.yaml", "config: value\n")

    destination_root = tmp_path / ".mirror" / "testuser"
    assert not destination_root.exists()

    init_user_home("testuser", templates_identity_root=templates_root, user_home=destination_root)

    assert destination_root.exists()
    assert (destination_root / "identity").exists()


def test_init_user_home_fails_when_identity_root_is_non_empty(tmp_path):
    templates_root = tmp_path / "templates" / "identity"
    _write_template(templates_root / "self" / "config.yaml", "config: value\n")

    destination_root = tmp_path / ".mirror" / "testuser"
    existing_identity_root = destination_root / "identity"
    _write_template(existing_identity_root / "self" / "soul.yaml", "existing: value\n")

    try:
        init_user_home(
            "testuser", templates_identity_root=templates_root, user_home=destination_root
        )
        raise AssertionError("Expected init_user_home() to fail for non-empty identity root")
    except FileExistsError as exc:
        assert "already exists" in str(exc)

    assert (existing_identity_root / "self" / "soul.yaml").read_text(
        encoding="utf-8"
    ) == "existing: value\n"


def test_init_user_home_fails_when_templates_are_missing(tmp_path):
    missing_templates_root = tmp_path / "templates" / "identity"
    destination_root = tmp_path / ".mirror" / "testuser"

    try:
        init_user_home(
            "testuser", templates_identity_root=missing_templates_root, user_home=destination_root
        )
        raise AssertionError("Expected init_user_home() to fail when templates are missing")
    except FileNotFoundError as exc:
        assert "templates" in str(exc)

    assert not destination_root.exists()


def test_find_templates_identity_root_finds_repo_templates(tmp_path):
    repo_root = tmp_path / "repo"
    templates_root = repo_root / "templates" / "identity"
    _write_template(templates_root / "self" / "config.yaml", "config: value\n")
    cli_file = repo_root / "src" / "memory" / "cli" / "init.py"
    cli_file.parent.mkdir(parents=True, exist_ok=True)
    cli_file.write_text("# placeholder\n", encoding="utf-8")

    found = find_templates_identity_root(cli_file)

    assert found == templates_root
