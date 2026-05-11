"""Tests for the Mirror Mode context dispatch helper."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

from memory.extensions.context import (
    collect_extension_context,
    render_sections,
)


@pytest.fixture
def mirror_home(tmp_path: Path, hello_fixture_dir: Path):
    """Build a mirror home with hello installed, schema migrated, one ping seeded."""
    home = tmp_path / "mirror"
    (home / "extensions").mkdir(parents=True)
    shutil.copytree(hello_fixture_dir, home / "extensions" / "hello")

    from memory.db.connection import get_connection
    from memory.extensions.migrations import run_migrations

    conn = get_connection(home / "memory.db")
    run_migrations(
        conn,
        extension_id="hello",
        migrations_dir=home / "extensions" / "hello" / "migrations",
    )
    conn.execute(
        "INSERT INTO ext_hello_pings (message, created_at) VALUES (?, ?)",
        ("alive", datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
    return home


def _bind(home: Path, capability: str, *, persona=None, journey=None) -> None:
    from memory.db.connection import get_connection

    conn = get_connection(home / "memory.db")
    target_kind, target_id = ("persona", persona) if persona else ("journey", journey)
    conn.execute(
        "INSERT INTO _ext_bindings VALUES (?, ?, ?, ?, ?)",
        (
            "hello",
            capability,
            target_kind,
            target_id,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def _open(home: Path):
    from memory.db.connection import get_connection

    return get_connection(home / "memory.db")


# --- Happy path -----------------------------------------------------------


def test_collects_persona_bound_section(mirror_home):
    _bind(mirror_home, "greeting", persona="tester")
    conn = _open(mirror_home)
    try:
        sections = collect_extension_context(
            conn,
            mirror_home=mirror_home,
            persona_id="tester",
            user="u",
        )
    finally:
        conn.close()
    assert len(sections) == 1
    s = sections[0]
    assert s.extension_id == "hello"
    assert s.capability_id == "greeting"
    assert s.binding_kind == "persona"
    assert s.binding_target == "tester"
    assert "Latest ping: alive" in s.text


def test_collects_journey_bound_section(mirror_home):
    _bind(mirror_home, "greeting", journey="eudaimon")
    conn = _open(mirror_home)
    try:
        sections = collect_extension_context(
            conn,
            mirror_home=mirror_home,
            persona_id=None,
            journey_id="eudaimon",
            user="u",
        )
    finally:
        conn.close()
    assert len(sections) == 1
    assert sections[0].binding_kind == "journey"
    assert sections[0].binding_target == "eudaimon"


def test_no_active_target_returns_empty(mirror_home):
    _bind(mirror_home, "greeting", persona="tester")
    conn = _open(mirror_home)
    try:
        sections = collect_extension_context(
            conn,
            mirror_home=mirror_home,
            persona_id=None,
            journey_id=None,
            user="u",
        )
    finally:
        conn.close()
    assert sections == []


def test_persona_mismatch_returns_empty(mirror_home):
    _bind(mirror_home, "greeting", persona="other")
    conn = _open(mirror_home)
    try:
        sections = collect_extension_context(
            conn,
            mirror_home=mirror_home,
            persona_id="tester",
            user="u",
        )
    finally:
        conn.close()
    assert sections == []


def test_provider_returning_none_is_skipped(tmp_path, hello_fixture_dir):
    """When the extension has no rows to report, its provider returns None
    and the section list stays empty."""
    home = tmp_path / "mirror"
    (home / "extensions").mkdir(parents=True)
    shutil.copytree(hello_fixture_dir, home / "extensions" / "hello")
    from memory.db.connection import get_connection
    from memory.extensions.migrations import run_migrations

    conn = get_connection(home / "memory.db")
    run_migrations(
        conn,
        extension_id="hello",
        migrations_dir=home / "extensions" / "hello" / "migrations",
    )
    conn.execute(
        "INSERT INTO _ext_bindings VALUES (?, ?, ?, ?, ?)",
        (
            "hello",
            "greeting",
            "persona",
            "tester",
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()

    sections = collect_extension_context(
        conn, mirror_home=home, persona_id="tester", user="u"
    )
    conn.close()
    assert sections == []


# --- Failure modes --------------------------------------------------------


def test_uninstalled_extension_logged_and_skipped(mirror_home, caplog):
    """A binding to an extension that is not on disk does not break the dispatch."""
    conn = _open(mirror_home)
    conn.execute(
        "INSERT INTO _ext_bindings VALUES (?, ?, ?, ?, ?)",
        (
            "ghost",
            "anything",
            "persona",
            "tester",
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    # Also bind hello so we know dispatch continues.
    conn.execute(
        "INSERT INTO _ext_bindings VALUES (?, ?, ?, ?, ?)",
        (
            "hello",
            "greeting",
            "persona",
            "tester",
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()

    with caplog.at_level("WARNING", logger="memory.extensions.context"):
        sections = collect_extension_context(
            conn, mirror_home=mirror_home, persona_id="tester", user="u"
        )
    conn.close()
    assert len(sections) == 1
    assert sections[0].extension_id == "hello"
    assert any("uninstalled extension" in rec.message for rec in caplog.records)


def test_provider_raising_is_caught(tmp_path, caplog):
    """A provider that raises does not break the dispatch."""
    home = tmp_path / "mirror"
    ext_dir = home / "extensions" / "boom"
    ext_dir.mkdir(parents=True)
    (ext_dir / "extension.py").write_text(
        "from memory.extensions.api import ExtensionAPI\n"
        "def register(api):\n"
        "    api.register_mirror_context('cap', _provide)\n"
        "def _provide(api, ctx):\n"
        "    raise RuntimeError('boom from provider')\n"
    )
    (ext_dir / "skill.yaml").write_text(
        "id: boom\n"
        "name: Boom\n"
        "category: extension\n"
        "kind: command-skill\n"
        "summary: provider raises\n"
        "entrypoint:\n  module: extension\n"
        "runtimes:\n  pi:\n    command_name: ext-boom\n"
        "mirror_context_providers:\n"
        "  - id: cap\n    description: x\n"
    )
    from memory.db.connection import get_connection

    conn = get_connection(home / "memory.db")
    conn.execute(
        "INSERT INTO _ext_bindings VALUES (?, ?, ?, ?, ?)",
        ("boom", "cap", "persona", "tester", datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()

    with caplog.at_level("WARNING", logger="memory.extensions.context"):
        sections = collect_extension_context(
            conn, mirror_home=home, persona_id="tester", user="u"
        )
    conn.close()
    assert sections == []
    assert any("provider raised" in rec.message for rec in caplog.records)


def test_binding_with_unknown_capability_is_skipped(mirror_home, caplog):
    _bind(mirror_home, "nonexistent_capability", persona="tester")
    conn = _open(mirror_home)
    with caplog.at_level("WARNING", logger="memory.extensions.context"):
        sections = collect_extension_context(
            conn, mirror_home=mirror_home, persona_id="tester", user="u"
        )
    conn.close()
    assert sections == []
    assert any("unknown capability" in rec.message for rec in caplog.records)


# --- Rendering ------------------------------------------------------------


def test_render_sections_concatenates_with_blank_line(mirror_home):
    _bind(mirror_home, "greeting", persona="tester")
    conn = _open(mirror_home)
    try:
        sections = collect_extension_context(
            conn, mirror_home=mirror_home, persona_id="tester", user="u"
        )
    finally:
        conn.close()
    text = render_sections(sections)
    assert "=== extension/hello/greeting ===" in text
    assert "Latest ping: alive" in text


def test_render_sections_empty_returns_empty_string():
    assert render_sections([]) == ""


# --- Stable ordering ------------------------------------------------------


def test_multiple_bindings_fire_in_stable_order(tmp_path, hello_fixture_dir):
    """Sections come out sorted by (extension_id, capability_id, ...)."""
    home = tmp_path / "mirror"
    (home / "extensions").mkdir(parents=True)
    shutil.copytree(hello_fixture_dir, home / "extensions" / "hello")
    # Add a second extension that also has a 'greeting' capability.
    ext2 = home / "extensions" / "echo"
    ext2.mkdir()
    (ext2 / "extension.py").write_text(
        "def register(api):\n"
        "    api.register_mirror_context('greeting', lambda a, c: 'from echo')\n"
    )
    (ext2 / "skill.yaml").write_text(
        "id: echo\n"
        "name: Echo\n"
        "category: extension\n"
        "kind: command-skill\n"
        "summary: x\n"
        "entrypoint:\n  module: extension\n"
        "runtimes:\n  pi:\n    command_name: ext-echo\n"
        "mirror_context_providers:\n"
        "  - id: greeting\n    description: x\n"
    )

    from memory.db.connection import get_connection
    from memory.extensions.migrations import run_migrations

    conn = get_connection(home / "memory.db")
    run_migrations(
        conn,
        extension_id="hello",
        migrations_dir=home / "extensions" / "hello" / "migrations",
    )
    conn.execute(
        "INSERT INTO ext_hello_pings (message, created_at) VALUES (?, ?)",
        ("alive", datetime.now(timezone.utc).isoformat()),
    )
    now = datetime.now(timezone.utc).isoformat()
    for extension_id in ("hello", "echo"):
        conn.execute(
            "INSERT INTO _ext_bindings VALUES (?, ?, ?, ?, ?)",
            (extension_id, "greeting", "persona", "tester", now),
        )
    conn.commit()

    sections = collect_extension_context(
        conn, mirror_home=home, persona_id="tester", user="u"
    )
    conn.close()
    assert [s.extension_id for s in sections] == ["echo", "hello"]
