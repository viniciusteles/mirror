"""Tests for legacy migration contract validation."""

import json
import sqlite3
from pathlib import Path

import pytest

from memory.cli.migrate_legacy import (
    _format_report,
    classify_source_db,
    inspect_source_db,
    run_migration,
    validate_migration,
    write_report,
)


def _write_sqlite_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE example (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()


def _columns(path: Path, table: str) -> set[str]:
    conn = sqlite3.connect(path)
    try:
        return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    finally:
        conn.close()


def _migrations(path: Path) -> set[str]:
    conn = sqlite3.connect(path)
    try:
        return {row[0] for row in conn.execute("SELECT id FROM _migrations")}
    finally:
        conn.close()


def _write_portuguese_legacy_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
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
        CREATE TABLE messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            role TEXT,
            content TEXT,
            created_at TEXT,
            token_count INTEGER,
            metadata TEXT
        );
        CREATE TABLE memories (
            id TEXT PRIMARY KEY,
            conversation_id TEXT,
            memory_type TEXT,
            layer TEXT,
            title TEXT,
            content TEXT,
            context TEXT,
            travessia TEXT,
            persona TEXT,
            tags TEXT,
            created_at TEXT,
            relevance_score REAL,
            embedding BLOB,
            metadata TEXT
        );
        CREATE TABLE tasks (
            id TEXT PRIMARY KEY,
            travessia TEXT,
            title TEXT,
            status TEXT,
            due_date TEXT,
            scheduled_at TEXT,
            time_hint TEXT,
            stage TEXT,
            context TEXT,
            source TEXT,
            created_at TEXT,
            updated_at TEXT,
            completed_at TEXT,
            metadata TEXT
        );
        CREATE TABLE attachments (
            id TEXT PRIMARY KEY,
            travessia_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            content TEXT NOT NULL,
            content_type TEXT,
            tags TEXT,
            embedding BLOB,
            created_at TEXT,
            updated_at TEXT,
            metadata TEXT
        );
        CREATE TABLE identity (
            id TEXT PRIMARY KEY,
            layer TEXT NOT NULL,
            key TEXT NOT NULL,
            content TEXT NOT NULL,
            version TEXT DEFAULT '1.0.0',
            created_at TEXT,
            updated_at TEXT,
            metadata TEXT
        );
        CREATE TABLE _migrations (id TEXT PRIMARY KEY, applied_at TEXT NOT NULL);
        CREATE INDEX idx_memories_travessia ON memories(travessia);
        CREATE INDEX idx_tasks_travessia ON tasks(travessia);
        CREATE INDEX idx_attachments_travessia ON attachments(travessia_id);
        CREATE UNIQUE INDEX idx_attachments_travessia_name ON attachments(travessia_id, name);
        INSERT INTO _migrations (id, applied_at)
        VALUES ('004_tasks_temporal_fields', '2026-04-18T00:00:00Z');
        INSERT INTO conversations (id, title, started_at, interface, persona, travessia)
        VALUES ('conv-1', 'Conversation', '2026-04-18T00:00:00Z', 'cli', 'engineer', 'mirror-poc');
        INSERT INTO messages (id, conversation_id, role, content, created_at)
        VALUES ('msg-1', 'conv-1', 'user', 'hello', '2026-04-18T00:00:01Z');
        INSERT INTO memories (id, conversation_id, memory_type, layer, title, content, travessia, created_at)
        VALUES ('mem-1', 'conv-1', 'decision', 'ego', 'Keep it', 'Content', 'mirror-poc', '2026-04-18T00:00:02Z');
        INSERT INTO tasks (id, travessia, title, status, source, created_at, updated_at)
        VALUES ('task-1', 'mirror-poc', 'Migrate schema', 'todo', 'manual', '2026-04-18T00:00:03Z', '2026-04-18T00:00:03Z');
        INSERT INTO attachments (id, travessia_id, name, content, created_at, updated_at)
        VALUES ('att-1', 'mirror-poc', 'plan.md', 'Plan', '2026-04-18T00:00:04Z', '2026-04-18T00:00:04Z');
        INSERT INTO identity (id, layer, key, content, created_at, updated_at)
        VALUES
            ('ident-1', 'travessia', 'mirror-poc', 'Journey identity', '2026-04-18T00:00:05Z', '2026-04-18T00:00:05Z'),
            ('ident-2', 'caminho', 'mirror-poc', 'Journey path', '2026-04-18T00:00:06Z', '2026-04-18T00:00:06Z');
        """
    )
    conn.commit()
    conn.close()


def _write_english_current_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE conversations (id TEXT PRIMARY KEY, journey TEXT);
        CREATE TABLE memories (id TEXT PRIMARY KEY, layer TEXT, journey TEXT);
        CREATE TABLE tasks (id TEXT PRIMARY KEY, journey TEXT);
        CREATE TABLE attachments (id TEXT PRIMARY KEY, journey_id TEXT);
        CREATE TABLE identity (id TEXT PRIMARY KEY, layer TEXT, key TEXT, content TEXT);
        CREATE TABLE _migrations (id TEXT PRIMARY KEY, applied_at TEXT NOT NULL);
        CREATE INDEX idx_memories_journey ON memories(journey);
        CREATE INDEX idx_tasks_journey ON tasks(journey);
        CREATE INDEX idx_attachments_journey ON attachments(journey_id);
        CREATE UNIQUE INDEX idx_attachments_journey_name ON attachments(journey_id, id);
        INSERT INTO _migrations (id, applied_at)
        VALUES ('005_travessia_to_journey', '2026-04-18T00:00:00Z');
        INSERT INTO identity (id, layer, key, content)
        VALUES ('ident-1', 'journey', 'mirror-poc', 'Journey identity');
        """
    )
    conn.commit()
    conn.close()


def _write_mixed_state_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE conversations (id TEXT PRIMARY KEY, journey TEXT);
        CREATE TABLE memories (id TEXT PRIMARY KEY, layer TEXT, travessia TEXT);
        CREATE TABLE tasks (id TEXT PRIMARY KEY, journey TEXT);
        CREATE TABLE attachments (id TEXT PRIMARY KEY, travessia_id TEXT);
        CREATE TABLE identity (id TEXT PRIMARY KEY, layer TEXT, key TEXT, content TEXT);
        CREATE TABLE _migrations (id TEXT PRIMARY KEY, applied_at TEXT NOT NULL);
        INSERT INTO identity (id, layer, key, content)
        VALUES
            ('ident-1', 'travessia', 'legacy', 'Legacy identity'),
            ('ident-2', 'journey', 'current', 'Current identity');
        """
    )
    conn.commit()
    conn.close()


def test_classify_source_db_returns_legacy_portuguese_for_supported_source(tmp_path):
    source_db = tmp_path / "legacy" / "memoria.db"
    _write_portuguese_legacy_db(source_db)

    assert classify_source_db(source_db) == "legacy_portuguese"


def test_inspect_source_db_returns_preflight_details_for_legacy_source(tmp_path):
    source_db = tmp_path / "legacy" / "memoria.db"
    _write_portuguese_legacy_db(source_db)

    details = inspect_source_db(source_db)

    assert details["source_db"] == source_db
    assert details["source_db_kind"] == "legacy_portuguese"
    assert details["tables_present"] == [
        "attachments",
        "conversations",
        "identity",
        "memories",
        "tasks",
    ]
    assert details["row_counts"]["conversations"] == 1
    assert details["row_counts"]["messages"] == 1
    assert details["row_counts"]["memories"] == 1
    assert details["legacy_columns_detected"] == {
        "attachments": "travessia_id",
        "conversations": "travessia",
        "memories": "travessia",
        "tasks": "travessia",
    }
    assert details["legacy_indexes_detected"] == [
        "idx_attachments_travessia",
        "idx_attachments_travessia_name",
        "idx_memories_travessia",
        "idx_tasks_travessia",
    ]
    assert details["legacy_identity_layers_detected"] == ["caminho", "travessia"]
    assert details["planned_translations"]["layers"] == {
        "travessia": "journey",
        "caminho": "journey_path",
    }


def test_validate_migration_returns_report_for_valid_source_and_target(tmp_path):
    source_db = tmp_path / "legacy" / "memoria.db"
    _write_portuguese_legacy_db(source_db)
    target_home = tmp_path / ".mirror" / "vinicius"

    report = validate_migration(source_db, target_home)

    assert report["source_db"] == source_db
    assert report["source_db_kind"] == "legacy_portuguese"
    assert report["source_row_counts"]["conversations"] == 1
    assert report["source_applied_migrations"] == ["004_tasks_temporal_fields"]
    assert report["legacy_identity_layers_detected"] == ["caminho", "travessia"]
    assert report["planned_translations"]["columns"]["attachments"] == (
        "travessia_id",
        "journey_id",
    )
    assert report["target_home"] == target_home
    assert report["target_db"] == target_home / "memory.db"
    assert report["target_home_exists"] is False
    assert report["target_identity_exists"] is False
    assert report["writes_planned"] is False


def test_write_report_serializes_validation_report_as_json(tmp_path):
    source_db = tmp_path / "legacy" / "memoria.db"
    _write_portuguese_legacy_db(source_db)
    target_home = tmp_path / ".mirror" / "vinicius"
    report_path = tmp_path / "reports" / "validate.json"

    report = validate_migration(source_db, target_home)
    written_path = write_report(report, report_path)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert written_path == report_path
    assert payload["command"] == "migrate-legacy validate"
    assert payload["source_db"] == str(source_db)
    assert payload["target_db"] == str(target_home / "memory.db")
    assert payload["source_db_kind"] == "legacy_portuguese"
    assert payload["planned_translations"]["layers"] == {
        "caminho": "journey_path",
        "travessia": "journey",
    }
    assert "generated_at" in payload


def test_format_report_includes_preflight_summary_and_translation_plan(tmp_path):
    source_db = tmp_path / "legacy" / "memoria.db"
    _write_portuguese_legacy_db(source_db)
    target_home = tmp_path / ".mirror" / "vinicius"

    report = validate_migration(source_db, target_home)
    formatted = _format_report(report)

    assert "Legacy migration validation succeeded." in formatted
    assert "Source DB kind: legacy_portuguese" in formatted
    assert "Source row counts:" in formatted
    assert "  - conversations: 1" in formatted
    assert "Legacy columns detected: attachments.travessia_id" in formatted
    assert "Legacy identity layers detected: caminho, travessia" in formatted
    assert "travessia -> journey" in formatted
    assert "caminho -> journey_path" in formatted
    assert "Writes planned: no" in formatted


def test_validate_migration_allows_existing_target_home_without_memory_db(tmp_path):
    source_db = tmp_path / "legacy" / "memoria.db"
    _write_portuguese_legacy_db(source_db)
    target_home = tmp_path / ".mirror" / "vinicius"
    (target_home / "identity").mkdir(parents=True)

    report = validate_migration(source_db, target_home)

    assert report["target_home_exists"] is True
    assert report["target_identity_exists"] is True
    assert report["target_db_exists"] is False


def test_validate_migration_fails_when_source_is_missing(tmp_path):
    source_db = tmp_path / "legacy" / "memoria.db"
    target_home = tmp_path / ".mirror" / "vinicius"

    with pytest.raises(FileNotFoundError) as exc_info:
        validate_migration(source_db, target_home)

    assert str(source_db) in str(exc_info.value)


def test_validate_migration_fails_when_source_is_not_a_sqlite_db(tmp_path):
    source_db = tmp_path / "legacy" / "memoria.db"
    source_db.parent.mkdir(parents=True, exist_ok=True)
    source_db.write_text("not a sqlite database", encoding="utf-8")
    target_home = tmp_path / ".mirror" / "vinicius"

    with pytest.raises(ValueError) as exc_info:
        validate_migration(source_db, target_home)

    assert "SQLite" in str(exc_info.value)


def test_validate_migration_fails_when_source_is_current_english_db(tmp_path):
    source_db = tmp_path / "legacy" / "memory.db"
    _write_english_current_db(source_db)
    target_home = tmp_path / ".mirror" / "vinicius"

    with pytest.raises(ValueError) as exc_info:
        validate_migration(source_db, target_home)

    assert "already uses the current English schema" in str(exc_info.value)


def test_validate_migration_fails_when_source_is_mixed_state_db(tmp_path):
    source_db = tmp_path / "legacy" / "mixed.db"
    _write_mixed_state_db(source_db)
    target_home = tmp_path / ".mirror" / "vinicius"

    with pytest.raises(ValueError) as exc_info:
        validate_migration(source_db, target_home)

    assert "mixed Portuguese/English state" in str(exc_info.value)


def test_validate_migration_fails_when_source_shape_is_unknown(tmp_path):
    source_db = tmp_path / "legacy" / "unknown.db"
    _write_sqlite_db(source_db)
    target_home = tmp_path / ".mirror" / "vinicius"

    with pytest.raises(ValueError) as exc_info:
        validate_migration(source_db, target_home)

    assert "unsupported schema shape" in str(exc_info.value)


def test_validate_migration_fails_when_target_home_is_a_file(tmp_path):
    source_db = tmp_path / "legacy" / "memoria.db"
    _write_portuguese_legacy_db(source_db)
    target_home = tmp_path / ".mirror" / "vinicius"
    target_home.parent.mkdir(parents=True, exist_ok=True)
    target_home.write_text("not a directory", encoding="utf-8")

    with pytest.raises(NotADirectoryError) as exc_info:
        validate_migration(source_db, target_home)

    assert str(target_home) in str(exc_info.value)


def test_validate_migration_fails_when_target_db_already_exists(tmp_path):
    source_db = tmp_path / "legacy" / "memoria.db"
    _write_portuguese_legacy_db(source_db)
    target_home = tmp_path / ".mirror" / "vinicius"
    target_db = target_home / "memory.db"
    _write_sqlite_db(target_db)

    with pytest.raises(FileExistsError) as exc_info:
        validate_migration(source_db, target_home)

    assert str(target_db) in str(exc_info.value)


def test_write_report_serializes_run_report_as_json(tmp_path):
    source_db = tmp_path / "legacy" / "memoria.db"
    _write_portuguese_legacy_db(source_db)
    target_home = tmp_path / ".mirror" / "vinicius"
    report_path = tmp_path / "reports" / "run.json"

    report = run_migration(source_db, target_home)
    written_path = write_report(report, report_path)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert written_path == report_path
    assert payload["command"] == "migrate-legacy run"
    assert payload["writes_performed"] is True
    assert payload["row_counts_after"]["conversations"] == 1
    assert "004_tasks_temporal_fields" in payload["target_applied_migrations"]
    assert "005_travessia_to_journey" in payload["target_applied_migrations"]
    assert payload["target_db"] == str(target_home / "memory.db")
    assert "generated_at" in payload


def test_run_migration_copies_source_to_target_and_migrates_schema(tmp_path):
    source_db = tmp_path / "legacy" / "memoria.db"
    _write_portuguese_legacy_db(source_db)
    target_home = tmp_path / ".mirror" / "vinicius"

    result = run_migration(source_db, target_home)

    target_db = target_home / "memory.db"
    assert result["source_db"] == source_db
    assert result["target_db"] == target_db
    assert result["writes_performed"] is True
    assert result["source_mutation_allowed"] is False
    assert result["copied_sidecars"] == []
    assert result["row_counts_before"]["conversations"] == 1
    assert result["row_counts_after"]["conversations"] == 1
    assert "journey" in _columns(target_db, "conversations")
    assert "travessia" not in _columns(target_db, "conversations")
    assert "journey_id" in _columns(target_db, "attachments")
    assert "travessia_id" not in _columns(target_db, "attachments")
    assert "005_travessia_to_journey" in _migrations(target_db)


def test_run_migration_preserves_the_legacy_source_unchanged(tmp_path):
    source_db = tmp_path / "legacy" / "memoria.db"
    _write_portuguese_legacy_db(source_db)
    target_home = tmp_path / ".mirror" / "vinicius"

    run_migration(source_db, target_home)

    assert "travessia" in _columns(source_db, "conversations")
    assert "journey" not in _columns(source_db, "conversations")
    assert "005_travessia_to_journey" not in _migrations(source_db)


def test_run_migration_copies_sqlite_sidecars_when_present(tmp_path):
    source_db = tmp_path / "legacy" / "memoria.db"
    _write_portuguese_legacy_db(source_db)
    source_wal = source_db.with_name("memoria.db-wal")
    source_shm = source_db.with_name("memoria.db-shm")
    source_wal.write_bytes(b"wal")
    source_shm.write_bytes(b"shm")
    target_home = tmp_path / ".mirror" / "vinicius"

    result = run_migration(source_db, target_home)

    copied_names = {Path(path).name for path in result["copied_sidecars"]}
    assert copied_names == {"memory.db-wal", "memory.db-shm"}
