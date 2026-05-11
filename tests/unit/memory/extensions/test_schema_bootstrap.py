"""Verifies that the extension bookkeeping tables ship with the core schema."""

from __future__ import annotations


def _columns(conn, table):
    return [row["name"] for row in conn.execute(f"PRAGMA table_info({table})")]


def test_ext_migrations_table_is_created(db_conn):
    cols = _columns(db_conn, "_ext_migrations")
    assert cols == ["extension_id", "filename", "checksum", "applied_at"]


def test_ext_bindings_table_is_created(db_conn):
    cols = _columns(db_conn, "_ext_bindings")
    assert cols == [
        "extension_id",
        "capability_id",
        "target_kind",
        "target_id",
        "created_at",
    ]


def test_ext_bindings_has_target_index(db_conn):
    rows = db_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='_ext_bindings'"
    ).fetchall()
    names = {row["name"] for row in rows}
    assert "idx_ext_bindings_target" in names


def test_ext_migrations_primary_key_is_extension_filename(db_conn):
    db_conn.execute(
        "INSERT INTO _ext_migrations VALUES (?, ?, ?, ?)",
        ("hello", "001_init.sql", "abc", "2026-05-11T00:00:00Z"),
    )
    # Inserting the same (extension_id, filename) again must fail on PK.
    import sqlite3

    import pytest

    with pytest.raises(sqlite3.IntegrityError):
        db_conn.execute(
            "INSERT INTO _ext_migrations VALUES (?, ?, ?, ?)",
            ("hello", "001_init.sql", "def", "2026-05-11T00:00:00Z"),
        )


def test_ext_bindings_allows_multiple_targets_for_same_capability(db_conn):
    db_conn.execute(
        "INSERT INTO _ext_bindings VALUES (?, ?, ?, ?, ?)",
        ("hello", "greeting", "persona", "writer", "2026-05-11T00:00:00Z"),
    )
    db_conn.execute(
        "INSERT INTO _ext_bindings VALUES (?, ?, ?, ?, ?)",
        ("hello", "greeting", "persona", "engineer", "2026-05-11T00:00:00Z"),
    )
    rows = db_conn.execute(
        "SELECT COUNT(*) AS c FROM _ext_bindings WHERE extension_id='hello'"
    ).fetchone()
    assert rows["c"] == 2
