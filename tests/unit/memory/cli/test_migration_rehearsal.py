"""Tests for rehearsing database migrations against a copied SQLite DB."""

import sqlite3

import pytest

from memory.cli.migration_rehearsal import (
    RehearsalVerificationError,
    _copy_database_files,
    main,
    rehearse_database_migration,
    resolve_production_db_path,
)


def _columns(db_path, table: str) -> set[str]:
    conn = sqlite3.connect(db_path)
    try:
        return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    finally:
        conn.close()


def _create_old_db(db_path) -> None:
    conn = sqlite3.connect(db_path)
    try:
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
                ('conv-1', 'Conversation', '2026-04-16T10:00:00Z', 'cli', 'engineer',
                 'mirror-poc');

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
        conn.commit()
    finally:
        conn.close()


def test_resolve_production_db_path_uses_configured_db_path(monkeypatch, tmp_path):
    db_path = tmp_path / "custom.db"
    monkeypatch.setenv("DB_PATH", str(db_path))

    assert resolve_production_db_path() == db_path


def test_resolve_production_db_path_uses_configured_production_dir(monkeypatch, tmp_path):
    prod_dir = tmp_path / "prod-memory"
    monkeypatch.delenv("DB_PATH", raising=False)
    monkeypatch.setenv("MEMORY_PROD_DIR", str(prod_dir))
    monkeypatch.setenv("MEMORY_DIR", str(tmp_path / "generic-memory"))

    assert resolve_production_db_path() == prod_dir / "memory.db"


def test_resolve_production_db_path_uses_configured_memory_dir(monkeypatch, tmp_path):
    memory_dir = tmp_path / "memory"
    monkeypatch.delenv("DB_PATH", raising=False)
    monkeypatch.delenv("MEMORY_PROD_DIR", raising=False)
    monkeypatch.setenv("MEMORY_DIR", str(memory_dir))

    assert resolve_production_db_path() == memory_dir / "memory.db"


def test_resolve_production_db_path_uses_mirror_dir_for_new_installs(monkeypatch, tmp_path):
    monkeypatch.delenv("DB_PATH", raising=False)
    monkeypatch.delenv("MEMORY_PROD_DIR", raising=False)
    monkeypatch.delenv("MEMORY_DIR", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))

    assert resolve_production_db_path() == tmp_path / ".mirror" / "memory.db"


def test_resolve_production_db_path_uses_existing_legacy_espelho_dir(monkeypatch, tmp_path):
    legacy_dir = tmp_path / ".espelho"
    legacy_dir.mkdir()
    monkeypatch.delenv("DB_PATH", raising=False)
    monkeypatch.delenv("MEMORY_PROD_DIR", raising=False)
    monkeypatch.delenv("MEMORY_DIR", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))

    assert resolve_production_db_path() == legacy_dir / "memory.db"


def test_resolve_production_db_path_prefers_existing_mirror_dir(monkeypatch, tmp_path):
    mirror_dir = tmp_path / ".mirror"
    legacy_dir = tmp_path / ".espelho"
    mirror_dir.mkdir()
    legacy_dir.mkdir()
    monkeypatch.delenv("DB_PATH", raising=False)
    monkeypatch.delenv("MEMORY_PROD_DIR", raising=False)
    monkeypatch.delenv("MEMORY_DIR", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))

    assert resolve_production_db_path() == mirror_dir / "memory.db"


def test_resolve_production_db_path_uses_legacy_db_name_when_needed(monkeypatch, tmp_path):
    memory_dir = tmp_path / "memory"
    legacy_db_path = memory_dir / "memoria.db"
    legacy_db_path.parent.mkdir()
    legacy_db_path.write_text("legacy db")
    monkeypatch.delenv("DB_PATH", raising=False)
    monkeypatch.delenv("MEMORY_PROD_DIR", raising=False)
    monkeypatch.setenv("MEMORY_DIR", str(memory_dir))

    assert resolve_production_db_path() == legacy_db_path


def test_rehearsal_migrates_copy_and_preserves_source_database(tmp_path):
    source = tmp_path / "memory.db"
    _create_old_db(source)

    result = rehearse_database_migration(source, output_dir=tmp_path / "rehearsals")

    assert result.source_db_path == source
    assert result.rehearsal_db_path.exists()
    assert result.rehearsal_db_path != source

    assert "travessia" in _columns(source, "conversations")
    assert "journey" not in _columns(source, "conversations")

    assert "journey" in _columns(result.rehearsal_db_path, "conversations")
    assert "travessia" not in _columns(result.rehearsal_db_path, "conversations")
    assert "journey_id" in _columns(result.rehearsal_db_path, "attachments")
    assert "travessia_id" not in _columns(result.rehearsal_db_path, "attachments")

    assert result.row_counts_before["conversations"] == 1
    assert result.row_counts_after["conversations"] == 1
    assert result.row_counts_before["memories"] == 2
    assert result.row_counts_after["memories"] == 2
    assert "005_travessia_to_journey" in result.applied_migrations


def test_rehearsal_verifies_english_indexes_and_layers(tmp_path):
    source = tmp_path / "memory.db"
    _create_old_db(source)

    result = rehearse_database_migration(source, output_dir=tmp_path / "rehearsals")

    assert "idx_memories_journey" in result.indexes
    assert "idx_tasks_journey" in result.indexes
    assert "idx_attachments_journey" in result.indexes
    assert "idx_attachments_journey_name" in result.indexes
    assert "idx_memories_travessia" not in result.indexes
    assert "idx_tasks_travessia" not in result.indexes
    assert "idx_attachments_travessia" not in result.indexes

    assert result.legacy_layer_counts == {"caminho": 0, "travessia": 0}


def test_copy_database_files_includes_sqlite_sidecars(tmp_path):
    source = tmp_path / "memory.db"
    source.write_text("db")
    source.with_name("memory.db-wal").write_text("wal")
    source.with_name("memory.db-shm").write_text("shm")

    copied = _copy_database_files(source, tmp_path / "copy")

    assert copied.db_path.read_text() == "db"
    assert copied.sidecars == (
        copied.db_path.with_name("memory.db-wal"),
        copied.db_path.with_name("memory.db-shm"),
    )
    assert copied.sidecars[0].read_text() == "wal"
    assert copied.sidecars[1].read_text() == "shm"


def test_rehearsal_fails_when_source_database_is_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        rehearse_database_migration(tmp_path / "missing.db", output_dir=tmp_path / "rehearsals")


def test_rehearsal_fails_when_verification_detects_unmigrated_schema(tmp_path, mocker):
    source = tmp_path / "memory.db"
    _create_old_db(source)
    mocker.patch("memory.cli.migration_rehearsal.get_connection")

    with pytest.raises(RehearsalVerificationError):
        rehearse_database_migration(source, output_dir=tmp_path / "rehearsals")


def test_main_reports_success_for_rehearsed_database(tmp_path, capsys):
    source = tmp_path / "memory.db"
    _create_old_db(source)

    exit_code = main(
        [
            "--db-path",
            str(source),
            "--output-dir",
            str(tmp_path / "rehearsals"),
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Migration rehearsal succeeded." in output
    assert "Source DB:" in output
    assert "Rehearsal DB:" in output
