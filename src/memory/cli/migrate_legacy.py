"""Validate the explicit contract for legacy migration into a user home."""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from memory.db.connection import get_connection

LEGACY_MIGRATION_ID = "005_travessia_to_journey"
_SUPPORTED_TABLES = ("conversations", "memories", "tasks", "attachments", "identity")
_ROW_COUNT_TABLES = (
    "conversations",
    "messages",
    "memories",
    "tasks",
    "attachments",
    "identity",
    "conversation_embeddings",
    "memory_access_log",
)
_LEGACY_COLUMN_MAP = {
    "conversations": ("travessia", "journey"),
    "memories": ("travessia", "journey"),
    "tasks": ("travessia", "journey"),
    "attachments": ("travessia_id", "journey_id"),
}
_LEGACY_INDEX_MAP = {
    "idx_memories_travessia": "idx_memories_journey",
    "idx_tasks_travessia": "idx_tasks_journey",
    "idx_attachments_travessia": "idx_attachments_journey",
    "idx_attachments_travessia_name": "idx_attachments_journey_name",
}
_LEGACY_LAYER_MAP = {
    "travessia": "journey",
    "caminho": "journey_path",
}
_EXPECTED_ENGLISH_COLUMNS = {
    "conversations": {"journey"},
    "memories": {"journey"},
    "tasks": {"journey"},
    "attachments": {"journey_id"},
}
_FORBIDDEN_LEGACY_COLUMNS = {
    "conversations": {"travessia"},
    "memories": {"travessia"},
    "tasks": {"travessia"},
    "attachments": {"travessia_id"},
}
_EXPECTED_ENGLISH_INDEXES = set(_LEGACY_INDEX_MAP.values())
_FORBIDDEN_LEGACY_INDEXES = set(_LEGACY_INDEX_MAP)


def _as_path(path: str | Path) -> Path:
    return Path(path).expanduser()


def _validate_source_db(source_db: Path) -> None:
    if not source_db.exists():
        raise FileNotFoundError(f"Legacy source database not found: {source_db}")
    if not source_db.is_file():
        raise FileNotFoundError(f"Legacy source database is not a file: {source_db}")

    try:
        with sqlite3.connect(f"file:{source_db}?mode=ro", uri=True) as conn:
            conn.execute("PRAGMA schema_version").fetchone()
    except sqlite3.DatabaseError as exc:
        raise ValueError(
            f"Legacy source database is not a readable SQLite database: {source_db}"
        ) from exc


def _validate_target_home(target_home: Path) -> None:
    if target_home.exists() and not target_home.is_dir():
        raise NotADirectoryError(f"Migration target home is not a directory: {target_home}")


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
    ).fetchone()
    return row is not None


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    if not _table_exists(conn, table):
        return set()
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row[1] for row in rows}


def _indexes(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'index'").fetchall()
    return {row[0] for row in rows}


def _applied_migrations(conn: sqlite3.Connection) -> set[str]:
    if not _table_exists(conn, "_migrations"):
        return set()
    rows = conn.execute("SELECT id FROM _migrations").fetchall()
    return {row[0] for row in rows}


def _row_counts(conn: sqlite3.Connection) -> dict[str, int]:
    counts = {}
    for table in _ROW_COUNT_TABLES:
        if _table_exists(conn, table):
            row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
            counts[table] = int(row[0])
    return counts


def inspect_source_db(source_db: str | Path) -> dict:
    resolved_source_db = _as_path(source_db)
    _validate_source_db(resolved_source_db)

    with sqlite3.connect(f"file:{resolved_source_db}?mode=ro", uri=True) as conn:
        tables_present = {table for table in _SUPPORTED_TABLES if _table_exists(conn, table)}
        columns = {table: _table_columns(conn, table) for table in _SUPPORTED_TABLES}
        indexes = _indexes(conn)
        migrations = _applied_migrations(conn)
        identity_layers = set()
        if _table_exists(conn, "identity"):
            identity_layers = {
                row[0] for row in conn.execute("SELECT DISTINCT layer FROM identity").fetchall()
            }
        row_counts = _row_counts(conn)

    portuguese_columns = (
        "travessia" in columns["conversations"]
        and "travessia" in columns["memories"]
        and "travessia" in columns["tasks"]
        and "travessia_id" in columns["attachments"]
    )
    english_columns = (
        "journey" in columns["conversations"]
        and "journey" in columns["memories"]
        and "journey" in columns["tasks"]
        and "journey_id" in columns["attachments"]
    )
    has_legacy_layers = bool(identity_layers & set(_LEGACY_LAYER_MAP))
    has_english_layers = bool(identity_layers & set(_LEGACY_LAYER_MAP.values()))
    has_legacy_indexes = bool(indexes & set(_LEGACY_INDEX_MAP))
    has_english_indexes = bool(indexes & set(_LEGACY_INDEX_MAP.values()))
    has_english_migration = LEGACY_MIGRATION_ID in migrations

    if (
        tables_present == set(_SUPPORTED_TABLES)
        and portuguese_columns
        and not english_columns
        and not has_english_layers
        and not has_english_migration
    ):
        source_db_kind = "legacy_portuguese"
    elif (
        english_columns and not portuguese_columns and (has_english_layers or has_english_migration)
    ):
        source_db_kind = "current_english"
    elif (
        (portuguese_columns and english_columns)
        or (has_legacy_layers and has_english_layers)
        or (
            has_english_migration
            and (portuguese_columns or has_legacy_layers or has_legacy_indexes)
        )
        or (has_legacy_indexes and has_english_indexes)
    ):
        source_db_kind = "mixed_state"
    else:
        source_db_kind = "unknown"

    return {
        "source_db": resolved_source_db,
        "source_db_kind": source_db_kind,
        "tables_present": sorted(tables_present),
        "row_counts": row_counts,
        "applied_migrations": sorted(migrations),
        "legacy_columns_detected": {
            table: legacy_name
            for table, (legacy_name, english_name) in _LEGACY_COLUMN_MAP.items()
            if legacy_name in columns[table] and english_name not in columns[table]
        },
        "legacy_indexes_detected": sorted(
            index_name for index_name in _LEGACY_INDEX_MAP if index_name in indexes
        ),
        "legacy_identity_layers_detected": sorted(
            layer_name for layer_name in _LEGACY_LAYER_MAP if layer_name in identity_layers
        ),
        "planned_translations": {
            "columns": dict(_LEGACY_COLUMN_MAP),
            "indexes": dict(_LEGACY_INDEX_MAP),
            "layers": dict(_LEGACY_LAYER_MAP),
        },
    }


def classify_source_db(source_db: str | Path) -> str:
    return inspect_source_db(source_db)["source_db_kind"]


def validate_migration(source_db: str | Path, target_home: str | Path) -> dict:
    resolved_source_db = _as_path(source_db)
    resolved_target_home = _as_path(target_home)
    target_db = resolved_target_home / "memory.db"
    target_identity_root = resolved_target_home / "identity"

    source_details = inspect_source_db(resolved_source_db)
    source_db_kind = source_details["source_db_kind"]
    _validate_target_home(resolved_target_home)

    if source_db_kind == "current_english":
        raise ValueError(
            f"Legacy migration source already uses the current English schema: {resolved_source_db}"
        )
    if source_db_kind == "mixed_state":
        raise ValueError(
            "Legacy migration source is in a mixed Portuguese/English state; refusing ambiguous migration: "
            f"{resolved_source_db}"
        )
    if source_db_kind != "legacy_portuguese":
        raise ValueError(
            f"Legacy migration source has an unsupported schema shape: {resolved_source_db}"
        )

    if target_db.exists():
        raise FileExistsError(
            f"Migration target database already exists; refusing to merge automatically: {target_db}"
        )

    return {
        "command": "migrate-legacy validate",
        "source_db": resolved_source_db,
        "source_db_kind": source_db_kind,
        "source_tables_present": source_details["tables_present"],
        "source_row_counts": source_details["row_counts"],
        "source_applied_migrations": source_details["applied_migrations"],
        "legacy_columns_detected": source_details["legacy_columns_detected"],
        "legacy_indexes_detected": source_details["legacy_indexes_detected"],
        "legacy_identity_layers_detected": source_details["legacy_identity_layers_detected"],
        "planned_translations": source_details["planned_translations"],
        "target_home": resolved_target_home,
        "target_db": target_db,
        "target_identity_root": target_identity_root,
        "source_mutation_allowed": False,
        "writes_planned": False,
        "target_home_exists": resolved_target_home.exists(),
        "target_identity_exists": target_identity_root.exists(),
        "target_db_exists": target_db.exists(),
    }


def _copy_source_db_to_target(source_db: Path, target_db: Path) -> list[Path]:
    target_db.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_db, target_db)

    copied_sidecars: list[Path] = []
    for suffix in ("-wal", "-shm"):
        source_sidecar = source_db.with_name(f"{source_db.name}{suffix}")
        if source_sidecar.exists():
            target_sidecar = target_db.with_name(f"{target_db.name}{suffix}")
            shutil.copy2(source_sidecar, target_sidecar)
            copied_sidecars.append(target_sidecar)
    return copied_sidecars


def _verify_migrated_target(target_db: Path, row_counts_before: dict[str, int]) -> dict:
    conn = sqlite3.connect(target_db)
    try:
        columns = {table: _table_columns(conn, table) for table in _EXPECTED_ENGLISH_COLUMNS}
        indexes = _indexes(conn)
        row_counts_after = _row_counts(conn)
        identity_layers = set()
        if _table_exists(conn, "identity"):
            identity_layers = {
                row[0] for row in conn.execute("SELECT DISTINCT layer FROM identity").fetchall()
            }
        migrations = _applied_migrations(conn)
    finally:
        conn.close()

    failures = []
    for table, expected in _EXPECTED_ENGLISH_COLUMNS.items():
        missing = expected - columns[table]
        if missing:
            failures.append(f"{table} missing expected columns: {', '.join(sorted(missing))}")
    for table, forbidden in _FORBIDDEN_LEGACY_COLUMNS.items():
        present = forbidden & columns[table]
        if present:
            failures.append(f"{table} still has legacy columns: {', '.join(sorted(present))}")

    missing_indexes = _EXPECTED_ENGLISH_INDEXES - indexes
    if missing_indexes:
        failures.append(f"missing expected indexes: {', '.join(sorted(missing_indexes))}")
    legacy_indexes = _FORBIDDEN_LEGACY_INDEXES & indexes
    if legacy_indexes:
        failures.append(f"legacy indexes still exist: {', '.join(sorted(legacy_indexes))}")

    for legacy_layer in _LEGACY_LAYER_MAP:
        if legacy_layer in identity_layers:
            failures.append(f"legacy identity layer remains: {legacy_layer}")
    if LEGACY_MIGRATION_ID not in migrations:
        failures.append(f"expected applied migration missing: {LEGACY_MIGRATION_ID}")

    changed_counts = {
        table: (before, row_counts_after.get(table))
        for table, before in row_counts_before.items()
        if row_counts_after.get(table) != before
    }
    if changed_counts:
        details = ", ".join(
            f"{table}: {before} -> {after}" for table, (before, after) in changed_counts.items()
        )
        failures.append(f"row counts changed: {details}")

    if failures:
        raise ValueError("Migrated target verification failed: " + "; ".join(failures))

    return {
        "row_counts_after": row_counts_after,
        "applied_migrations": sorted(migrations),
        "identity_layers": sorted(identity_layers),
    }


def run_migration(source_db: str | Path, target_home: str | Path) -> dict:
    validation = validate_migration(source_db, target_home)
    target_db = validation["target_db"]
    copied_sidecars = _copy_source_db_to_target(validation["source_db"], target_db)

    migrated_conn = get_connection(target_db)
    migrated_conn.close()

    verification = _verify_migrated_target(target_db, validation["source_row_counts"])

    return {
        **validation,
        "command": "migrate-legacy run",
        "writes_planned": True,
        "writes_performed": True,
        "copied_sidecars": [str(path) for path in copied_sidecars],
        "row_counts_before": validation["source_row_counts"],
        "row_counts_after": verification["row_counts_after"],
        "target_applied_migrations": verification["applied_migrations"],
        "target_identity_layers": verification["identity_layers"],
    }


def _json_ready(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_ready(item) for item in value]
    return value


def write_report(report: dict[str, Any], destination: str | Path) -> Path:
    report_path = _as_path(destination)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        **_json_ready(report),
    }
    report_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report_path


def _format_report(report: dict) -> str:
    lines = [
        "Legacy migration validation succeeded."
        if report["command"] == "migrate-legacy validate"
        else "Legacy migration run succeeded.",
        f"Source DB: {report['source_db']}",
        f"Source DB kind: {report['source_db_kind']}",
        f"Target home: {report['target_home']}",
        f"Target DB: {report['target_db']}",
        f"Target identity root: {report['target_identity_root']}",
        f"Target home exists: {'yes' if report['target_home_exists'] else 'no'}",
        f"Target identity exists: {'yes' if report['target_identity_exists'] else 'no'}",
        "Source tables present: " + ", ".join(report["source_tables_present"]),
        "Source row counts:",
        *[f"  - {table}: {count}" for table, count in sorted(report["source_row_counts"].items())],
        "Applied migrations: "
        + (
            ", ".join(report["source_applied_migrations"])
            if report["source_applied_migrations"]
            else "none"
        ),
        "Legacy columns detected: "
        + (
            ", ".join(
                f"{table}.{column}"
                for table, column in sorted(report["legacy_columns_detected"].items())
            )
            if report["legacy_columns_detected"]
            else "none"
        ),
        "Legacy indexes detected: "
        + (
            ", ".join(report["legacy_indexes_detected"])
            if report["legacy_indexes_detected"]
            else "none"
        ),
        "Legacy identity layers detected: "
        + (
            ", ".join(report["legacy_identity_layers_detected"])
            if report["legacy_identity_layers_detected"]
            else "none"
        ),
        "Planned translations:",
        *[
            f"  - {legacy} -> {english}"
            for legacy, english in sorted(report["planned_translations"]["columns"].values())
        ],
        *[
            f"  - {legacy} -> {english}"
            for legacy, english in sorted(report["planned_translations"]["indexes"].items())
        ],
        *[
            f"  - {legacy} -> {english}"
            for legacy, english in sorted(report["planned_translations"]["layers"].items())
        ],
    ]

    if report["command"] == "migrate-legacy run":
        lines.extend(
            [
                "Copied sidecars: "
                + (
                    ", ".join(Path(path).name for path in report["copied_sidecars"])
                    if report["copied_sidecars"]
                    else "none"
                ),
                "Target row counts after migration:",
                *[
                    f"  - {table}: {count}"
                    for table, count in sorted(report["row_counts_after"].items())
                ],
                "Target applied migrations: "
                + (
                    ", ".join(report["target_applied_migrations"])
                    if report["target_applied_migrations"]
                    else "none"
                ),
                "Target identity layers: "
                + (
                    ", ".join(report["target_identity_layers"])
                    if report["target_identity_layers"]
                    else "none"
                ),
                "Writes planned: yes",
                "Writes performed: yes",
                "Source mutation allowed: no",
            ]
        )
    else:
        lines.extend(
            [
                "Writes planned: no",
                "Source mutation allowed: no",
            ]
        )

    if report.get("report_path") is not None:
        lines.append(f"Report written to: {report['report_path']}")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Validate the explicit contract for legacy migration into a user home"
    )
    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser(
        "validate", description="Validate source and target for a future legacy migration"
    )
    validate_parser.add_argument("--source", required=True, help="Path to the legacy SQLite DB")
    validate_parser.add_argument(
        "--target-home", required=True, help="Target user home under ~/.mirror/<user>"
    )
    validate_parser.add_argument(
        "--report", default=None, help="Write the validation report to a JSON file"
    )

    run_parser = subparsers.add_parser(
        "run", description="Copy and migrate a supported legacy source into a user home"
    )
    run_parser.add_argument("--source", required=True, help="Path to the legacy SQLite DB")
    run_parser.add_argument(
        "--target-home", required=True, help="Target user home under ~/.mirror/<user>"
    )
    run_parser.add_argument("--report", default=None, help="Write the run report to a JSON file")

    args = parser.parse_args(argv)

    if args.command not in {"validate", "run"}:
        parser.print_help()
        sys.exit(1)

    try:
        report = (
            validate_migration(args.source, args.target_home)
            if args.command == "validate"
            else run_migration(args.source, args.target_home)
        )
        if args.report is not None:
            report["report_path"] = write_report(report, args.report)
    except (FileNotFoundError, NotADirectoryError, ValueError, FileExistsError, OSError) as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    print(_format_report(report))


if __name__ == "__main__":
    main()
