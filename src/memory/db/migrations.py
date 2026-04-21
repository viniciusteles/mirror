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


MigrationApply = Callable[[sqlite3.Connection], None]


MIGRATIONS: list[tuple[str, MigrationApply]] = [
    ("001_project_to_travessia", _migrate_project_to_travessia),
    ("002_create_attachments", _migrate_create_attachments),
    ("003_create_tasks", _migrate_create_tasks),
    ("004_tasks_temporal_fields", _migrate_tasks_temporal_fields),
    ("005_travessia_to_journey", _migrate_travessia_to_journey),
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
