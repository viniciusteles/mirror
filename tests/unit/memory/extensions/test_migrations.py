"""Tests for the SQL migration runner."""

from __future__ import annotations

import pytest

from memory.extensions.errors import ExtensionMigrationError
from memory.extensions.migrations import run_migrations, table_prefix_for


def _write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_table_prefix_uses_underscored_id():
    assert table_prefix_for("hello") == "ext_hello_"
    assert table_prefix_for("review-copy") == "ext_review_copy_"


def test_run_migrations_applies_pending_files(db_conn, tmp_path):
    migrations = tmp_path / "migrations"
    _write(
        migrations / "001_init.sql",
        "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY, msg TEXT);",
    )

    applied = run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)

    assert applied == 1
    rows = db_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='ext_hello_pings'"
    ).fetchall()
    assert len(rows) == 1
    recorded = db_conn.execute(
        "SELECT filename, checksum FROM _ext_migrations WHERE extension_id='hello'"
    ).fetchall()
    assert [row["filename"] for row in recorded] == ["001_init.sql"]
    assert recorded[0]["checksum"]  # non-empty


def test_run_migrations_is_idempotent(db_conn, tmp_path):
    migrations = tmp_path / "migrations"
    _write(
        migrations / "001_init.sql",
        "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY);",
    )

    first = run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)
    second = run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)

    assert first == 1
    assert second == 0


def test_run_migrations_applies_files_in_lexicographic_order(db_conn, tmp_path):
    migrations = tmp_path / "migrations"
    _write(
        migrations / "002_add_col.sql",
        "ALTER TABLE ext_hello_pings ADD COLUMN created_at TEXT;",
    )
    _write(
        migrations / "001_init.sql",
        "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY);",
    )

    applied = run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)
    assert applied == 2
    cols = [row["name"] for row in db_conn.execute("PRAGMA table_info(ext_hello_pings)")]
    assert "created_at" in cols


def test_run_migrations_rejects_table_outside_prefix(db_conn, tmp_path):
    migrations = tmp_path / "migrations"
    _write(migrations / "001_init.sql", "CREATE TABLE memories (id INTEGER PRIMARY KEY);")

    with pytest.raises(ExtensionMigrationError) as excinfo:
        run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)
    assert "memories" in str(excinfo.value)
    assert "ext_hello_" in str(excinfo.value)


def test_run_migrations_rejects_dml_outside_prefix(db_conn, tmp_path):
    migrations = tmp_path / "migrations"
    _write(
        migrations / "001_init.sql",
        "CREATE TABLE ext_hello_x (id INTEGER PRIMARY KEY);\nINSERT INTO memories (id) VALUES (1);",
    )

    with pytest.raises(ExtensionMigrationError):
        run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)


def test_run_migrations_accepts_seed_dml_for_own_tables(db_conn, tmp_path):
    migrations = tmp_path / "migrations"
    _write(
        migrations / "001_init.sql",
        "CREATE TABLE ext_hello_categories (name TEXT PRIMARY KEY);\n"
        "INSERT INTO ext_hello_categories (name) VALUES ('default');",
    )

    run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)
    rows = db_conn.execute("SELECT name FROM ext_hello_categories").fetchall()
    assert [row["name"] for row in rows] == ["default"]


def test_run_migrations_rejects_index_on_outside_table(db_conn, tmp_path):
    migrations = tmp_path / "migrations"
    _write(
        migrations / "001_init.sql",
        "CREATE INDEX evil ON memories(title);",
    )

    with pytest.raises(ExtensionMigrationError):
        run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)


def test_run_migrations_detects_checksum_mismatch(db_conn, tmp_path):
    migrations = tmp_path / "migrations"
    initial = migrations / "001_init.sql"
    _write(initial, "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY);")
    run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)

    # Edit the applied file. Re-run must refuse.
    initial.write_text(
        "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY, extra TEXT);",
        encoding="utf-8",
    )
    with pytest.raises(ExtensionMigrationError) as excinfo:
        run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)
    msg = str(excinfo.value)
    assert "edited" in msg or "checksum" in msg


def test_run_migrations_rolls_back_on_failure(db_conn, tmp_path):
    migrations = tmp_path / "migrations"
    _write(
        migrations / "001_init.sql",
        "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY);\n"
        "INSERT INTO ext_hello_pings (id, missing_column) VALUES (1, 'x');",
    )

    with pytest.raises(ExtensionMigrationError):
        run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)

    # Neither the table creation nor the bookkeeping row may have persisted.
    tables = db_conn.execute(
        "SELECT name FROM sqlite_master WHERE name='ext_hello_pings'"
    ).fetchall()
    assert tables == []
    recorded = db_conn.execute(
        "SELECT * FROM _ext_migrations WHERE extension_id='hello'"
    ).fetchall()
    assert recorded == []


def test_run_migrations_rejects_invalid_filename(db_conn, tmp_path):
    migrations = tmp_path / "migrations"
    _write(migrations / "init.sql", "CREATE TABLE ext_hello_x (id INTEGER);")

    with pytest.raises(ExtensionMigrationError) as excinfo:
        run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)
    assert "invalid migration filename" in str(excinfo.value)


def test_run_migrations_with_missing_directory_is_noop(db_conn, tmp_path):
    applied = run_migrations(
        db_conn, extension_id="hello", migrations_dir=tmp_path / "does-not-exist"
    )
    assert applied == 0


def test_extension_id_with_dash_maps_to_underscored_prefix(db_conn, tmp_path):
    migrations = tmp_path / "migrations"
    _write(
        migrations / "001_init.sql",
        "CREATE TABLE ext_review_copy_reports (id INTEGER PRIMARY KEY);",
    )

    applied = run_migrations(db_conn, extension_id="review-copy", migrations_dir=migrations)

    assert applied == 1
