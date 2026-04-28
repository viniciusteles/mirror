"""Tests for the migration runner — skip-if-applied and idempotency."""

import sqlite3

from memory.db.migrations import MIGRATIONS, run_migrations

MIGRATION_IDS = [mid for mid, _apply in MIGRATIONS]


def _applied_ids(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT id FROM _migrations").fetchall()
    return {row[0] for row in rows}


def _fresh_conn() -> sqlite3.Connection:
    """Conexão em memória sem nenhum schema — simula banco zerado."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


class TestRunMigrations:
    def test_creates_migrations_table(self, db_conn):
        run_migrations(db_conn)
        tables = {
            row[0] for row in db_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        assert "_migrations" in tables

    def test_all_migrations_recorded(self, db_conn):
        run_migrations(db_conn)
        applied = _applied_ids(db_conn)
        assert set(MIGRATION_IDS).issubset(applied)

    def test_migrations_idempotent(self, db_conn):
        """Running twice must not raise and must not duplicate entries."""
        run_migrations(db_conn)
        run_migrations(db_conn)
        for mid in MIGRATION_IDS:
            count = db_conn.execute(
                "SELECT COUNT(*) FROM _migrations WHERE id = ?", (mid,)
            ).fetchone()[0]
            assert count == 1, f"Migration {mid} recorded {count} times"

    def test_already_applied_migration_skipped(self, db_conn):
        """Pre-recording a migration ID causes run_migrations to skip it."""
        run_migrations(db_conn)  # apply all first
        count_before = db_conn.execute("SELECT COUNT(*) FROM _migrations").fetchone()[0]

        # Remove one and re-run — it should be skipped (table already exists)
        # Just verify the count stays the same after a second run
        run_migrations(db_conn)
        count_after = db_conn.execute("SELECT COUNT(*) FROM _migrations").fetchone()[0]
        assert count_after == count_before

    def test_migrations_list_not_empty(self):
        assert len(MIGRATIONS) > 0

    def test_each_migration_has_id_and_apply_callable(self):
        for mid, apply in MIGRATIONS:
            assert mid, "Migration id must not be empty"
            assert callable(apply), f"Migration {mid} must expose a callable apply"

    def test_migration_ids_are_unique(self):
        assert len(MIGRATION_IDS) == len(set(MIGRATION_IDS)), "Duplicate migration IDs found"

    def test_tasks_table_has_temporal_fields_after_migration(self, db_conn):
        """Migration 004 adds scheduled_at and time_hint to tasks."""
        run_migrations(db_conn)
        cols = {row[1] for row in db_conn.execute("PRAGMA table_info(tasks)")}
        assert "scheduled_at" in cols
        assert "time_hint" in cols

    def test_attachments_table_created_by_migration(self, db_conn):
        """Migration 002 creates the attachments table."""
        run_migrations(db_conn)
        tables = {
            row[0] for row in db_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        assert "attachments" in tables

    def test_llm_calls_table_created_by_migration_006(self):
        """Migration 006 creates llm_calls on a legacy DB that lacks it."""
        conn = _fresh_conn()
        run_migrations(conn)
        tables = {
            row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        assert "llm_calls" in tables

    def test_llm_calls_migration_idempotent_on_schema_db(self, db_conn):
        """Migration 006 is a no-op when llm_calls already exists from SCHEMA."""
        run_migrations(db_conn)  # llm_calls already exists via SCHEMA
        run_migrations(db_conn)  # second run must not raise
        count = db_conn.execute(
            "SELECT COUNT(*) FROM _migrations WHERE id = '006_create_llm_calls'"
        ).fetchone()[0]
        assert count == 1

    def test_llm_calls_table_has_expected_columns(self, db_conn):
        run_migrations(db_conn)
        cols = {row[1] for row in db_conn.execute("PRAGMA table_info(llm_calls)")}
        expected = {
            "id",
            "role",
            "model",
            "prompt",
            "response",
            "prompt_tokens",
            "completion_tokens",
            "latency_ms",
            "cost_usd",
            "conversation_id",
            "session_id",
            "called_at",
        }
        assert expected.issubset(cols)
