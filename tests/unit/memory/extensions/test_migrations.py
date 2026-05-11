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


# --- CV14.E2.S3: checksum tolerates comment and whitespace edits ----


def test_adding_a_line_comment_does_not_trip_checksum_guard(db_conn, tmp_path):
    """Documentation should never be hostile. Adding a `-- note` to an
    already-applied migration must be a no-op on the next run.
    """
    migrations = tmp_path / "migrations"
    initial = migrations / "001_init.sql"
    _write(initial, "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY);")
    run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)

    # Append a comment. Semantically identical SQL.
    initial.write_text(
        "-- a clarifying note added after the fact\n"
        "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY);\n",
        encoding="utf-8",
    )
    applied = run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)
    assert applied == 0


def test_block_comment_does_not_trip_checksum_guard(db_conn, tmp_path):
    migrations = tmp_path / "migrations"
    initial = migrations / "001_init.sql"
    _write(initial, "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY);")
    run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)

    initial.write_text(
        "/* multi-line\n   block comment */\n"
        "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY);\n",
        encoding="utf-8",
    )
    applied = run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)
    assert applied == 0


def test_whitespace_changes_do_not_trip_checksum_guard(db_conn, tmp_path):
    """Reformatting (extra blank lines, indentation, trailing spaces)
    must be tolerated."""
    migrations = tmp_path / "migrations"
    initial = migrations / "001_init.sql"
    _write(initial, "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY);")
    run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)

    initial.write_text(
        "\n\nCREATE TABLE ext_hello_pings (\n    id INTEGER PRIMARY KEY\n);\n\n",
        encoding="utf-8",
    )
    applied = run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)
    assert applied == 0


def test_structural_change_still_trips_checksum_guard(db_conn, tmp_path):
    """The relaxation is comments+whitespace only. Any real change to
    the SQL (new column, different table name, value drift) must
    still be rejected."""
    migrations = tmp_path / "migrations"
    initial = migrations / "001_init.sql"
    _write(initial, "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY);")
    run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)

    initial.write_text(
        "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY, extra TEXT);\n",
        encoding="utf-8",
    )
    with pytest.raises(ExtensionMigrationError):
        run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)


def test_string_literal_change_still_trips_checksum_guard(db_conn, tmp_path):
    """String literals are SQL content, not commentary. Editing one is
    a structural change and must trip the guard."""
    migrations = tmp_path / "migrations"
    initial = migrations / "001_init.sql"
    _write(
        initial,
        "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY, label TEXT);\n"
        "INSERT INTO ext_hello_pings (id, label) VALUES (1, 'alpha');\n",
    )
    run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)

    initial.write_text(
        "CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY, label TEXT);\n"
        "INSERT INTO ext_hello_pings (id, label) VALUES (1, 'beta');\n",
        encoding="utf-8",
    )
    with pytest.raises(ExtensionMigrationError):
        run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)


def test_legacy_raw_checksum_is_silently_upgraded(db_conn, tmp_path):
    """Backwards-compat: a row recorded under the old raw-bytes scheme
    that still matches the file as-is must be accepted and silently
    upgraded to the normalised checksum on the next run.
    """
    import hashlib

    migrations = tmp_path / "migrations"
    initial = migrations / "001_init.sql"
    sql = "-- pre-existing migration\nCREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY);"
    _write(initial, sql)

    # Hand-write the bookkeeping the way pre-S3 code would have: hash
    # of the raw bytes, no normalisation. The table itself is created
    # below so the migration can be "already applied".
    db_conn.execute("CREATE TABLE ext_hello_pings (id INTEGER PRIMARY KEY)")
    raw_checksum = hashlib.sha256(sql.encode("utf-8")).hexdigest()
    db_conn.execute(
        "INSERT INTO _ext_migrations (extension_id, filename, checksum, applied_at) "
        "VALUES (?, ?, ?, ?)",
        ("hello", "001_init.sql", raw_checksum, "2026-01-01T00:00:00Z"),
    )
    db_conn.commit()

    # Re-run: should accept, upgrade the stored checksum to the
    # normalised one, and report zero newly applied files.
    applied = run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)
    assert applied == 0

    stored = db_conn.execute(
        "SELECT checksum FROM _ext_migrations WHERE extension_id='hello'"
    ).fetchone()["checksum"]
    assert stored != raw_checksum  # upgraded

    # And a subsequent run is still a clean no-op.
    applied = run_migrations(db_conn, extension_id="hello", migrations_dir=migrations)
    assert applied == 0


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
