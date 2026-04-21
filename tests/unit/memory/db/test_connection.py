"""Unit tests for memory.db.connection."""

import sqlite3

import pytest

from memory.db.connection import get_connection

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_db_path(tmp_path):
    return tmp_path / "test.db"


# ---------------------------------------------------------------------------
# get_connection
# ---------------------------------------------------------------------------


class TestGetConnection:
    def test_returns_sqlite_connection(self, tmp_db_path):
        conn = get_connection(db_path=tmp_db_path)
        try:
            assert isinstance(conn, sqlite3.Connection)
        finally:
            conn.close()

    def test_row_factory_is_sqlite_row(self, tmp_db_path):
        conn = get_connection(db_path=tmp_db_path)
        try:
            assert conn.row_factory is sqlite3.Row
        finally:
            conn.close()

    def test_creates_parent_directory(self, tmp_path):
        nested = tmp_path / "new_dir" / "sub" / "memory.db"
        conn = get_connection(db_path=nested)
        try:
            assert nested.parent.exists()
            assert isinstance(conn, sqlite3.Connection)
        finally:
            conn.close()

    def test_wal_mode_enabled(self, tmp_db_path):
        conn = get_connection(db_path=tmp_db_path)
        try:
            row = conn.execute("PRAGMA journal_mode").fetchone()
            assert row[0] == "wal"
        finally:
            conn.close()

    def test_foreign_keys_enabled(self, tmp_db_path):
        conn = get_connection(db_path=tmp_db_path)
        try:
            row = conn.execute("PRAGMA foreign_keys").fetchone()
            assert row[0] == 1
        finally:
            conn.close()

    def test_schema_applied_to_new_db(self, tmp_db_path):
        conn = get_connection(db_path=tmp_db_path)
        conn.close()
        conn2 = sqlite3.connect(str(tmp_db_path))
        try:
            row = conn2.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='conversations'"
            ).fetchone()
            assert row[0] == 1
        finally:
            conn2.close()

    def test_migrations_run_on_every_open(self, tmp_db_path, mocker):
        # SCHEMA is idempotent and migrations are idempotent, so we always run
        # both. Concurrent openers used to race on a split "new vs existing"
        # decision; that branching was removed in the CV5.E2.S2 follow-up.
        conn = get_connection(db_path=tmp_db_path)
        conn.close()
        mock_migrations = mocker.patch("memory.db.connection.run_migrations")
        conn2 = get_connection(db_path=tmp_db_path)
        conn2.close()
        mock_migrations.assert_called_once()

    def test_migrations_run_on_fresh_db(self, tmp_db_path, mocker):
        mock_migrations = mocker.patch("memory.db.connection.run_migrations")
        conn = get_connection(db_path=tmp_db_path)
        conn.close()
        mock_migrations.assert_called_once()

    def test_second_connection_to_same_path_works(self, tmp_db_path):
        conn1 = get_connection(db_path=tmp_db_path)
        conn1.close()
        conn2 = get_connection(db_path=tmp_db_path)
        try:
            row = conn2.execute("SELECT 1").fetchone()
            assert row[0] == 1
        finally:
            conn2.close()
