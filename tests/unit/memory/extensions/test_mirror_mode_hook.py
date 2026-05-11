"""End-to-end tests for the Mirror Mode -> extensions hook.

These tests build an actual IdentityService against a temporary mirror
home and confirm that:

  * when a persona has an extension capability bound, the provider's
    text appears in load_mirror_context output with the canonical
    '=== extension/<id>/<capability> ===' header;

  * when nothing is bound, the prompt is unaffected;

  * a provider failure does not break Mirror Mode.
"""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest


@pytest.fixture
def mirror_home(tmp_path: Path, hello_fixture_dir: Path, monkeypatch) -> Path:
    """Set up a temp home, install hello fixture, point MIRROR_HOME at it."""
    home = tmp_path / "mirror" / "test-user"
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
        ("from hook test", datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()

    monkeypatch.setenv("MIRROR_HOME", str(home))
    monkeypatch.delenv("MIRROR_USER", raising=False)
    return home


def _service(mirror_home: Path):
    from memory.db.connection import get_connection
    from memory.services.attachment import AttachmentService
    from memory.services.identity import IdentityService
    from memory.storage.store import Store

    conn = get_connection(mirror_home / "memory.db")
    store = Store(conn)
    return IdentityService(store=store, attachments=AttachmentService(store))


def _seed_persona(service, persona_id="tester") -> None:
    service.set_identity("persona", persona_id, "I am the tester persona.")


def _bind(mirror_home: Path, persona_id: str = "tester") -> None:
    from memory.db.connection import get_connection

    conn = get_connection(mirror_home / "memory.db")
    conn.execute(
        "INSERT INTO _ext_bindings VALUES (?, ?, ?, ?, ?)",
        (
            "hello",
            "greeting",
            "persona",
            persona_id,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def test_bound_provider_appears_in_mirror_context(mirror_home):
    service = _service(mirror_home)
    _seed_persona(service)
    _bind(mirror_home)

    context = service.load_mirror_context(persona="tester")
    assert "=== extension/hello/greeting ===" in context
    assert "Latest ping: from hook test" in context


def test_no_binding_means_no_extension_section(mirror_home):
    service = _service(mirror_home)
    _seed_persona(service)
    # do NOT bind

    context = service.load_mirror_context(persona="tester")
    assert "extension/hello" not in context


def test_no_persona_means_no_extension_section(mirror_home):
    service = _service(mirror_home)
    _bind(mirror_home)

    context = service.load_mirror_context()  # no persona
    assert "extension/hello" not in context


def test_provider_failure_does_not_break_mirror_mode(tmp_path, monkeypatch):
    """If the bound provider raises, load_mirror_context still returns
    its core sections."""
    home = tmp_path / "mirror" / "test-user"
    ext_dir = home / "extensions" / "boom"
    ext_dir.mkdir(parents=True)
    (ext_dir / "extension.py").write_text(
        "def register(api):\n"
        "    api.register_mirror_context('cap', _provide)\n"
        "def _provide(api, ctx):\n"
        "    raise RuntimeError('crash')\n"
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
    conn.close()

    monkeypatch.setenv("MIRROR_HOME", str(home))
    monkeypatch.delenv("MIRROR_USER", raising=False)

    from memory.db.connection import get_connection as get_conn
    from memory.services.attachment import AttachmentService
    from memory.services.identity import IdentityService
    from memory.storage.store import Store

    conn = get_conn(home / "memory.db")
    store = Store(conn)
    service = IdentityService(store=store, attachments=AttachmentService(store))
    service.set_identity("persona", "tester", "I am the tester persona.")

    # Must not raise.
    context = service.load_mirror_context(persona="tester")
    # No extension section was produced.
    assert "extension/boom" not in context
    # Core persona section is still there.
    assert "persona/tester" in context
