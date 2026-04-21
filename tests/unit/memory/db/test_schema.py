"""Testes do schema SQLite — criação e idempotência."""

import sqlite3

import pytest

from memory.db.schema import SCHEMA

EXPECTED_TABLES = {
    "conversations",
    "messages",
    "memories",
    "conversation_embeddings",
    "memory_access_log",
    "tasks",
    "identity",
}


def _get_tables(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return {row[0] for row in rows}


class TestSchema:
    def test_all_expected_tables_created(self, db_conn):
        tables = _get_tables(db_conn)
        assert EXPECTED_TABLES.issubset(tables)

    def test_schema_is_idempotent(self, db_conn):
        """Executar o schema duas vezes não deve lançar erro."""
        db_conn.executescript(SCHEMA)
        tables = _get_tables(db_conn)
        assert EXPECTED_TABLES.issubset(tables)

    def test_conversations_columns(self, db_conn):
        cols = {row[1] for row in db_conn.execute("PRAGMA table_info(conversations)")}
        assert {"id", "title", "started_at", "interface", "journey"}.issubset(cols)
        assert "travessia" not in cols

    def test_memories_has_embedding_column(self, db_conn):
        cols = {row[1] for row in db_conn.execute("PRAGMA table_info(memories)")}
        assert "embedding" in cols
        assert "journey" in cols
        assert "travessia" not in cols

    def test_identity_has_unique_layer_key(self, db_conn):
        db_conn.execute(
            "INSERT INTO identity (id, layer, key, content, created_at, updated_at) "
            "VALUES ('1', 'ego', 'identity', 'x', '2024-01-01', '2024-01-01')"
        )
        with pytest.raises(sqlite3.IntegrityError):
            db_conn.execute(
                "INSERT INTO identity (id, layer, key, content, created_at, updated_at) "
                "VALUES ('2', 'ego', 'identity', 'y', '2024-01-01', '2024-01-01')"
            )

    def test_tasks_has_temporal_fields(self, db_conn):
        cols = {row[1] for row in db_conn.execute("PRAGMA table_info(tasks)")}
        assert {"scheduled_at", "time_hint"}.issubset(cols)
        assert "journey" in cols
        assert "travessia" not in cols

    def test_attachments_use_journey_id(self, db_conn):
        cols = {row[1] for row in db_conn.execute("PRAGMA table_info(attachments)")}
        assert "journey_id" in cols
        assert "travessia_id" not in cols
