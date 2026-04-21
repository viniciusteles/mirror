"""Tests for migrating persisted Portuguese schema names to English."""

import sqlite3

from memory.db.migrations import run_migrations


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def _indexes(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'index'").fetchall()
    return {row[0] for row in rows}


def _old_schema_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(
        """
        CREATE TABLE conversations (
            id TEXT PRIMARY KEY,
            title TEXT,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            interface TEXT NOT NULL,
            persona TEXT,
            travessia TEXT,
            summary TEXT,
            tags TEXT,
            metadata TEXT
        );

        CREATE TABLE memories (
            id TEXT PRIMARY KEY,
            conversation_id TEXT REFERENCES conversations(id),
            memory_type TEXT NOT NULL,
            layer TEXT NOT NULL DEFAULT 'ego',
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            context TEXT,
            travessia TEXT,
            persona TEXT,
            tags TEXT,
            created_at TEXT NOT NULL,
            relevance_score REAL DEFAULT 1.0,
            embedding BLOB,
            metadata TEXT
        );

        CREATE TABLE identity (
            id TEXT PRIMARY KEY,
            layer TEXT NOT NULL,
            key TEXT NOT NULL,
            content TEXT NOT NULL,
            version TEXT DEFAULT '1.0.0',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            metadata TEXT,
            UNIQUE(layer, key)
        );

        CREATE TABLE tasks (
            id TEXT PRIMARY KEY,
            travessia TEXT,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'todo',
            due_date TEXT,
            scheduled_at TEXT,
            time_hint TEXT,
            stage TEXT,
            context TEXT,
            source TEXT NOT NULL DEFAULT 'manual',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            completed_at TEXT,
            metadata TEXT
        );

        CREATE TABLE attachments (
            id TEXT PRIMARY KEY,
            travessia_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            content TEXT NOT NULL,
            content_type TEXT NOT NULL DEFAULT 'markdown',
            tags TEXT,
            embedding BLOB,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            metadata TEXT
        );

        CREATE INDEX idx_memories_travessia ON memories(travessia);
        CREATE INDEX idx_tasks_travessia ON tasks(travessia);
        CREATE INDEX idx_attachments_travessia ON attachments(travessia_id);
        CREATE UNIQUE INDEX idx_attachments_travessia_name
            ON attachments(travessia_id, name);

        INSERT INTO conversations
            (id, title, started_at, interface, persona, travessia)
        VALUES
            ('conv-1', 'Conversation', '2026-04-16T10:00:00Z', 'cli', 'engineer', 'mirror-poc');

        INSERT INTO memories
            (id, conversation_id, memory_type, layer, title, content, context,
             travessia, created_at)
        VALUES
            ('mem-1', 'conv-1', 'decision', 'travessia', 'Decision', 'Keep data',
             'context', 'mirror-poc', '2026-04-16T10:01:00Z'),
            ('mem-2', 'conv-1', 'insight', 'caminho', 'Path', 'Keep path',
             'context', 'mirror-poc', '2026-04-16T10:02:00Z');

        INSERT INTO identity
            (id, layer, key, content, created_at, updated_at)
        VALUES
            ('ident-1', 'travessia', 'mirror-poc', 'Journey identity',
             '2026-04-16T10:03:00Z', '2026-04-16T10:03:00Z'),
            ('ident-2', 'caminho', 'mirror-poc', 'Journey path',
             '2026-04-16T10:04:00Z', '2026-04-16T10:04:00Z');

        INSERT INTO tasks
            (id, travessia, title, status, source, created_at, updated_at)
        VALUES
            ('task-1', 'mirror-poc', 'Migrate schema', 'todo', 'manual',
             '2026-04-16T10:05:00Z', '2026-04-16T10:05:00Z');

        INSERT INTO attachments
            (id, travessia_id, name, content, created_at, updated_at)
        VALUES
            ('att-1', 'mirror-poc', 'plan.md', 'Plan',
             '2026-04-16T10:06:00Z', '2026-04-16T10:06:00Z');
        """
    )
    return conn


class TestEnglishSchemaMigration:
    def test_renames_portuguese_columns_and_preserves_values(self):
        conn = _old_schema_conn()
        try:
            run_migrations(conn)

            assert "journey" in _columns(conn, "conversations")
            assert "travessia" not in _columns(conn, "conversations")
            assert "journey" in _columns(conn, "memories")
            assert "travessia" not in _columns(conn, "memories")
            assert "journey" in _columns(conn, "tasks")
            assert "travessia" not in _columns(conn, "tasks")
            assert "journey_id" in _columns(conn, "attachments")
            assert "travessia_id" not in _columns(conn, "attachments")

            conversation = conn.execute(
                "SELECT journey FROM conversations WHERE id = 'conv-1'"
            ).fetchone()
            memory = conn.execute("SELECT journey FROM memories WHERE id = 'mem-1'").fetchone()
            task = conn.execute("SELECT journey FROM tasks WHERE id = 'task-1'").fetchone()
            attachment = conn.execute(
                "SELECT journey_id FROM attachments WHERE id = 'att-1'"
            ).fetchone()

            assert conversation["journey"] == "mirror-poc"
            assert memory["journey"] == "mirror-poc"
            assert task["journey"] == "mirror-poc"
            assert attachment["journey_id"] == "mirror-poc"
        finally:
            conn.close()

    def test_renames_indexes_to_english_names(self):
        conn = _old_schema_conn()
        try:
            run_migrations(conn)

            indexes = _indexes(conn)
            assert "idx_memories_journey" in indexes
            assert "idx_tasks_journey" in indexes
            assert "idx_attachments_journey" in indexes
            assert "idx_attachments_journey_name" in indexes
            assert "idx_memories_travessia" not in indexes
            assert "idx_tasks_travessia" not in indexes
            assert "idx_attachments_travessia" not in indexes
            assert "idx_attachments_travessia_name" not in indexes
        finally:
            conn.close()

    def test_migrates_identity_layers_to_english(self):
        conn = _old_schema_conn()
        try:
            run_migrations(conn)

            layers = {
                row["layer"]
                for row in conn.execute(
                    "SELECT layer FROM identity WHERE key = 'mirror-poc' ORDER BY layer"
                )
            }
            memory_layers = {
                row["layer"]
                for row in conn.execute(
                    "SELECT layer FROM memories WHERE conversation_id = 'conv-1' ORDER BY layer"
                )
            }

            assert {"journey", "journey_path"}.issubset(layers)
            assert "travessia" not in layers
            assert "caminho" not in layers
            assert {"journey", "journey_path"}.issubset(memory_layers)
            assert "travessia" not in memory_layers
            assert "caminho" not in memory_layers
        finally:
            conn.close()
