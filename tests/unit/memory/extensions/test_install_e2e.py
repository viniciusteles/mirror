"""End-to-end test for `extensions install` of a command-skill.

Confirms the full chain documented in
docs/product/extensions/architecture.md: copy source tree, run SQL
migrations, validate by importing extension.py and calling register(),
sync runtime SKILL.md files into <mirror_home>/runtime/skills/<rt>/.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from memory.cli.extensions import (
    ExtensionValidationError,
    install_extension,
)


@pytest.fixture
def source_root(tmp_path: Path, hello_fixture_dir: Path) -> Path:
    """Stage the hello fixture in a 'source' directory the way a user repo
    would look."""
    root = tmp_path / "sources"
    root.mkdir()
    shutil.copytree(hello_fixture_dir, root / "hello")
    return root


@pytest.fixture
def mirror_home(tmp_path: Path) -> Path:
    home = tmp_path / "mirror" / "test-user"
    home.mkdir(parents=True)
    return home


def test_install_copies_runs_migrations_and_validates_register(source_root, mirror_home):
    result = install_extension("hello", source_root=source_root, mirror_home=mirror_home)

    # Source tree copied.
    installed = mirror_home / "extensions" / "hello"
    assert installed.exists()
    assert (installed / "extension.py").exists()
    assert (installed / "migrations" / "001_init.sql").exists()

    # Migrations applied.
    assert result["migrations_applied"] == 1
    assert result["register_validated"] is True
    from memory.db.connection import get_connection

    conn = get_connection(mirror_home / "memory.db")
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='ext_hello_pings'"
    ).fetchall()
    conn.close()
    assert len(rows) == 1

    # Runtime SKILL.md surfaces created for every declared runtime.
    pi_skill = mirror_home / "runtime" / "skills" / "pi" / "ext-hello" / "SKILL.md"
    claude_skill = mirror_home / "runtime" / "skills" / "claude" / "ext:hello" / "SKILL.md"
    assert pi_skill.exists()
    assert claude_skill.exists()


def test_install_is_idempotent_on_migrations(source_root, mirror_home):
    install_extension("hello", source_root=source_root, mirror_home=mirror_home)
    second = install_extension("hello", source_root=source_root, mirror_home=mirror_home)
    assert second["migrations_applied"] == 0
    assert second["register_validated"] is True


def test_install_surfaces_migration_failure_as_validation_error(tmp_path, mirror_home):
    """A migration that violates the prefix is reported as a validation
    error from the install path so the CLI shows a single error type."""
    src = tmp_path / "sources"
    bad = src / "bad"
    (bad / "migrations").mkdir(parents=True)
    (bad / "extension.py").write_text("def register(api):\n    pass\n")
    (bad / "skill.yaml").write_text(
        "id: bad\n"
        "name: Bad\n"
        "category: extension\n"
        "kind: command-skill\n"
        "summary: bad prefix\n"
        "entrypoint:\n  module: extension\n"
        "runtimes:\n  pi:\n    command_name: ext-bad\n"
    )
    (bad / "migrations" / "001_init.sql").write_text(
        "CREATE TABLE memories_extra (id INTEGER PRIMARY KEY);"
    )

    with pytest.raises(ExtensionValidationError) as excinfo:
        install_extension("bad", source_root=src, mirror_home=mirror_home)
    assert "migrations failed" in str(excinfo.value)


def test_install_surfaces_register_failure_as_validation_error(tmp_path, mirror_home):
    src = tmp_path / "sources"
    boom = src / "boom"
    boom.mkdir(parents=True)
    (boom / "extension.py").write_text(
        "def register(api):\n    raise RuntimeError('failed on purpose')\n"
    )
    (boom / "skill.yaml").write_text(
        "id: boom\n"
        "name: Boom\n"
        "category: extension\n"
        "kind: command-skill\n"
        "summary: register raises\n"
        "entrypoint:\n  module: extension\n"
        "runtimes:\n  pi:\n    command_name: ext-boom\n"
    )

    with pytest.raises(ExtensionValidationError) as excinfo:
        install_extension("boom", source_root=src, mirror_home=mirror_home)
    assert "register(api) failed" in str(excinfo.value)


def test_uninstall_removes_bindings_but_preserves_data_tables(source_root, mirror_home):
    """A full uninstall should sweep the binding rows that point at the
    departing extension (otherwise Mirror Mode logs warnings on every
    turn) but must leave the extension's own data tables intact.
    The user can run a separate purge later if they really want the
    rows gone.
    """
    from memory.cli.extensions import uninstall_extension
    from memory.db.connection import get_connection

    install_extension("hello", source_root=source_root, mirror_home=mirror_home)

    # Seed a row in the data table and a binding.
    conn = get_connection(mirror_home / "memory.db")
    conn.execute(
        "INSERT INTO ext_hello_pings (message, created_at) VALUES (?, ?)",
        ("survive me", "2026-05-11T00:00:00Z"),
    )
    conn.execute(
        "INSERT INTO _ext_bindings VALUES (?, ?, ?, ?, ?)",
        ("hello", "greeting", "persona", "tester", "2026-05-11T00:00:00Z"),
    )
    conn.commit()
    conn.close()

    result = uninstall_extension("hello", mirror_home=mirror_home)
    assert result["bindings_removed"] == 1

    conn = get_connection(mirror_home / "memory.db")
    try:
        # Bindings: gone.
        rows = conn.execute(
            "SELECT COUNT(*) AS c FROM _ext_bindings WHERE extension_id='hello'"
        ).fetchone()
        assert rows["c"] == 0
        # Data table: still present, with the row preserved.
        rows = conn.execute("SELECT message FROM ext_hello_pings").fetchall()
        assert [r["message"] for r in rows] == ["survive me"]
    finally:
        conn.close()


def test_install_prompt_skill_does_not_touch_db(tmp_path, mirror_home):
    """prompt-skill extensions install without running migrations or
    importing any module."""
    src = tmp_path / "sources"
    prompt = src / "prompt"
    prompt.mkdir(parents=True)
    (prompt / "SKILL.md").write_text("# Prompt\n")
    (prompt / "skill.yaml").write_text(
        "id: prompt\n"
        "name: Prompt\n"
        "category: extension\n"
        "kind: prompt-skill\n"
        "summary: pure prompt\n"
        "runtimes:\n"
        "  pi:\n    command_name: ext-prompt\n    skill_file: SKILL.md\n"
    )

    result = install_extension("prompt", source_root=src, mirror_home=mirror_home)
    assert result["migrations_applied"] == 0
    assert result["register_validated"] is False
    # No memory.db is created when nothing required it.
    assert not (mirror_home / "memory.db").exists()
