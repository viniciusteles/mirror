"""Incremental database migrations.

Every migration is idempotent: running it twice is a no-op, and running it
against a fresh database that was already initialized from SCHEMA is also a
no-op. Migrations do NOT silently swallow errors — a genuine failure raises.

This matters under concurrent startup: when two processes race to initialize
the same database, SCHEMA and migrations each may have been partially applied
by the other process. Both layers must tolerate that without masking real
bugs.
"""

import sqlite3
from collections.abc import Callable

from memory.models import _now


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row[1] for row in rows}


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
    ).fetchone()
    return row is not None


def _rename_column_if_needed(
    conn: sqlite3.Connection, table: str, old_name: str, new_name: str
) -> None:
    if not _table_exists(conn, table):
        return
    columns = _table_columns(conn, table)
    if new_name in columns:
        return
    if old_name not in columns:
        return
    conn.execute(f"ALTER TABLE {table} RENAME COLUMN {old_name} TO {new_name}")


def _add_column_if_missing(
    conn: sqlite3.Connection, table: str, column: str, column_type: str
) -> None:
    if not _table_exists(conn, table):
        return
    columns = _table_columns(conn, table)
    if column in columns:
        return
    conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")


# --- Migration apply functions (all idempotent) ---


def _migrate_project_to_travessia(conn: sqlite3.Connection) -> None:
    """Rename legacy `project` columns to `travessia` (Portuguese-era intermediate)."""
    _rename_column_if_needed(conn, "conversations", "project", "travessia")
    _rename_column_if_needed(conn, "memories", "project", "travessia")
    conn.execute("DROP INDEX IF EXISTS idx_memories_project")
    # Index on travessia is dropped again by migration 005; create only if the
    # column still exists so we don't break on modern schemas.
    if _table_exists(conn, "memories") and "travessia" in _table_columns(conn, "memories"):
        conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_travessia ON memories(travessia)")
    if _table_exists(conn, "identity"):
        conn.execute("UPDATE identity SET layer = 'travessia' WHERE layer = 'project'")


def _migrate_create_attachments(conn: sqlite3.Connection) -> None:
    """Create the attachments table if legacy init never did."""
    if _table_exists(conn, "attachments"):
        return
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS attachments (
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
        CREATE INDEX IF NOT EXISTS idx_attachments_travessia
            ON attachments(travessia_id);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_attachments_travessia_name
            ON attachments(travessia_id, name);
        """
    )


def _migrate_create_tasks(conn: sqlite3.Connection) -> None:
    """Create the tasks table if legacy init never did."""
    if _table_exists(conn, "tasks"):
        return
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            travessia TEXT,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'todo',
            due_date TEXT,
            stage TEXT,
            context TEXT,
            source TEXT NOT NULL DEFAULT 'manual',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            completed_at TEXT,
            metadata TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_tasks_travessia ON tasks(travessia);
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
        """
    )


def _migrate_tasks_temporal_fields(conn: sqlite3.Connection) -> None:
    """Add scheduled_at / time_hint to tasks if missing."""
    _add_column_if_missing(conn, "tasks", "scheduled_at", "TEXT")
    _add_column_if_missing(conn, "tasks", "time_hint", "TEXT")


def _migrate_travessia_to_journey(conn: sqlite3.Connection) -> None:
    """Rename persisted journey terminology from Portuguese to English."""
    conn.executescript(
        """
        DROP INDEX IF EXISTS idx_memories_travessia;
        DROP INDEX IF EXISTS idx_tasks_travessia;
        DROP INDEX IF EXISTS idx_attachments_travessia;
        DROP INDEX IF EXISTS idx_attachments_travessia_name;
        """
    )

    _rename_column_if_needed(conn, "conversations", "travessia", "journey")
    _rename_column_if_needed(conn, "memories", "travessia", "journey")
    _rename_column_if_needed(conn, "tasks", "travessia", "journey")
    _rename_column_if_needed(conn, "attachments", "travessia_id", "journey_id")

    if _table_exists(conn, "identity"):
        conn.execute("UPDATE identity SET layer = 'journey' WHERE layer = 'travessia'")
        conn.execute("UPDATE identity SET layer = 'journey_path' WHERE layer = 'caminho'")

    if _table_exists(conn, "memories"):
        conn.execute("UPDATE memories SET layer = 'journey' WHERE layer = 'travessia'")
        conn.execute("UPDATE memories SET layer = 'journey_path' WHERE layer = 'caminho'")

    if _table_exists(conn, "memories") and "journey" in _table_columns(conn, "memories"):
        conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_journey ON memories(journey)")
    if _table_exists(conn, "tasks") and "journey" in _table_columns(conn, "tasks"):
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_journey ON tasks(journey)")
    if _table_exists(conn, "attachments") and "journey_id" in _table_columns(conn, "attachments"):
        conn.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_attachments_journey ON attachments(journey_id);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_attachments_journey_name
                ON attachments(journey_id, name);
            """
        )


def _migrate_create_llm_calls(conn: sqlite3.Connection) -> None:
    """Create the llm_calls table if it does not yet exist."""
    if _table_exists(conn, "llm_calls"):
        return
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS llm_calls (
            id TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            model TEXT NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            latency_ms INTEGER,
            cost_usd REAL,
            conversation_id TEXT REFERENCES conversations(id),
            session_id TEXT,
            called_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_llm_calls_conversation ON llm_calls(conversation_id);
        CREATE INDEX IF NOT EXISTS idx_llm_calls_role ON llm_calls(role);
        CREATE INDEX IF NOT EXISTS idx_llm_calls_called_at ON llm_calls(called_at);
        """
    )


def _migrate_create_memories_fts(conn: sqlite3.Connection) -> None:
    """Create the memories_fts FTS5 table, triggers, and initial population.

    Skipped on fresh databases where `memories` does not exist yet — SCHEMA
    creates memories_fts alongside the other tables in that case.
    """
    if _table_exists(conn, "memories_fts"):
        return
    if not _table_exists(conn, "memories"):
        # Fresh database: SCHEMA will create memories_fts when it runs after migrations.
        return
    conn.executescript(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
            title,
            content,
            context,
            content=memories,
            content_rowid=rowid
        );

        CREATE TRIGGER IF NOT EXISTS memories_fts_ai AFTER INSERT ON memories BEGIN
            INSERT INTO memories_fts(rowid, title, content, context)
            VALUES (NEW.rowid, NEW.title, NEW.content, COALESCE(NEW.context, ''));
        END;

        CREATE TRIGGER IF NOT EXISTS memories_fts_ad AFTER DELETE ON memories BEGIN
            INSERT INTO memories_fts(memories_fts, rowid, title, content, context)
            VALUES ('delete', OLD.rowid, OLD.title, OLD.content, COALESCE(OLD.context, ''));
        END;

        CREATE TRIGGER IF NOT EXISTS memories_fts_au AFTER UPDATE ON memories BEGIN
            INSERT INTO memories_fts(memories_fts, rowid, title, content, context)
            VALUES ('delete', OLD.rowid, OLD.title, OLD.content, COALESCE(OLD.context, ''));
            INSERT INTO memories_fts(rowid, title, content, context)
            VALUES (NEW.rowid, NEW.title, NEW.content, COALESCE(NEW.context, ''));
        END;

        INSERT INTO memories_fts(rowid, title, content, context)
        SELECT rowid, title, content, COALESCE(context, '') FROM memories;
        """
    )


def _migrate_create_identity_descriptors(conn: sqlite3.Connection) -> None:
    """Create the identity_descriptors sidecar table if it does not yet exist."""
    if _table_exists(conn, "identity_descriptors"):
        return
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS identity_descriptors (
            layer        TEXT NOT NULL,
            key          TEXT NOT NULL,
            descriptor   TEXT NOT NULL,
            generated_at TEXT NOT NULL,
            PRIMARY KEY (layer, key)
        );
        """
    )


MigrationApply = Callable[[sqlite3.Connection], None]


MIGRATIONS: list[tuple[str, MigrationApply]] = [
    ("001_project_to_travessia", _migrate_project_to_travessia),
    ("002_create_attachments", _migrate_create_attachments),
    ("003_create_tasks", _migrate_create_tasks),
    ("004_tasks_temporal_fields", _migrate_tasks_temporal_fields),
    ("005_travessia_to_journey", _migrate_travessia_to_journey),
    ("006_create_llm_calls", _migrate_create_llm_calls),
    ("007_create_identity_descriptors", _migrate_create_identity_descriptors),
    ("008_create_memories_fts", _migrate_create_memories_fts),
]


def run_migrations(conn: sqlite3.Connection) -> None:
    """Run any pending migrations against an existing database.

    Each migration is idempotent, so running this against a database that was
    already bootstrapped from SCHEMA is safe and a no-op.
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS _migrations (
            id TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )
    conn.commit()

    for migration_id, apply in MIGRATIONS:
        row = conn.execute("SELECT id FROM _migrations WHERE id = ?", (migration_id,)).fetchone()
        if row:
            continue
        try:
            apply(conn)
        except Exception:
            conn.rollback()
            raise
        conn.execute(
            "INSERT OR IGNORE INTO _migrations (id, applied_at) VALUES (?, ?)",
            (migration_id, _now()),
        )
        conn.commit()
