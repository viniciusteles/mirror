"""SQL migration runner for extensions.

Each extension owns its own SQL migration files under ``migrations/``.
This module applies pending files in lexicographic order, tracks what
has been applied in ``_ext_migrations``, and enforces the table-prefix
contract documented in ``docs/product/extensions/migrations.md``:

  * every DDL statement must target tables matching ``ext_<id>_*``;
  * each migration runs inside a single transaction (atomic);
  * applied migrations are pinned by SHA-256 checksum, so editing a
    file already on disk is detected and refused.

The runner is intentionally conservative: any deviation from the
contract raises :class:`ExtensionMigrationError` without leaving the
database half-written.
"""

from __future__ import annotations

import hashlib
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from memory.extensions.errors import ExtensionMigrationError

_FILENAME_RE = re.compile(r"^\d{3,}_[a-z0-9_]+\.sql$")

# Match DDL/DML that targets a named table. Captures the table name in the
# first group. We strip strings/comments before applying the regex so a
# stray "create table" inside a string literal does not trip us up.
_DDL_TABLE_RE = re.compile(
    r"""
    \b(?:
        CREATE\s+(?:VIRTUAL\s+)?TABLE        |
        ALTER\s+TABLE                        |
        DROP\s+TABLE                         |
        INSERT\s+(?:OR\s+\w+\s+)?INTO        |
        UPDATE                               |
        DELETE\s+FROM
    )
    \s+(?:IF\s+(?:NOT\s+)?EXISTS\s+)?
    "?([A-Za-z_][A-Za-z0-9_]*)"?
    """,
    re.IGNORECASE | re.VERBOSE,
)

_INDEX_TABLE_RE = re.compile(
    r"""
    \bCREATE\s+(?:UNIQUE\s+)?INDEX\s+
    (?:IF\s+NOT\s+EXISTS\s+)?
    (?:"?[A-Za-z_][A-Za-z0-9_]*"?\s+)?
    ON\s+
    "?([A-Za-z_][A-Za-z0-9_]*)"?
    """,
    re.IGNORECASE | re.VERBOSE,
)

_STRIP_COMMENTS_RE = re.compile(r"--[^\n]*|/\*.*?\*/", re.DOTALL)
_STRIP_STRINGS_RE = re.compile(r"'(?:[^']|'')*'")


def _strip_noise(sql: str) -> str:
    """Remove comments and string literals before structural inspection."""
    return _STRIP_STRINGS_RE.sub("''", _STRIP_COMMENTS_RE.sub("", sql))


def _split_statements(sql: str) -> list[str]:
    """Split a migration script into individual statements.

    SQLite's ``executescript`` commits any open transaction before
    running, which breaks atomicity. We split the script ourselves and
    feed each statement through ``conn.execute`` inside a single
    explicit transaction, so a mid-script failure rolls everything
    back, including the bookkeeping row.

    The splitter is intentionally simple: it respects single-quoted
    string literals and ``--`` / ``/* ... */`` comments. It does not
    support compound statements (``BEGIN ... END``); migration scripts
    do not need them.
    """
    statements: list[str] = []
    buffer: list[str] = []
    i = 0
    n = len(sql)
    while i < n:
        ch = sql[i]
        if ch == "-" and i + 1 < n and sql[i + 1] == "-":
            # Line comment runs to end of line; drop it.
            end = sql.find("\n", i)
            i = n if end == -1 else end
            continue
        if ch == "/" and i + 1 < n and sql[i + 1] == "*":
            end = sql.find("*/", i + 2)
            i = n if end == -1 else end + 2
            continue
        if ch == "'":
            # Walk to the matching close quote, honouring ''-escapes.
            buffer.append(ch)
            i += 1
            while i < n:
                buffer.append(sql[i])
                if sql[i] == "'":
                    if i + 1 < n and sql[i + 1] == "'":
                        buffer.append(sql[i + 1])
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            continue
        if ch == ";":
            stmt = "".join(buffer).strip()
            if stmt:
                statements.append(stmt)
            buffer = []
            i += 1
            continue
        buffer.append(ch)
        i += 1
    tail = "".join(buffer).strip()
    if tail:
        statements.append(tail)
    return statements


def _extract_table_targets(sql: str) -> list[str]:
    """Return every table name this SQL statement reads or writes to.

    Conservative: misses very exotic syntax, but covers all DDL and DML
    shapes extensions are allowed to use.
    """
    cleaned = _strip_noise(sql)
    tables = [m.group(1).lower() for m in _DDL_TABLE_RE.finditer(cleaned)]
    tables.extend(m.group(1).lower() for m in _INDEX_TABLE_RE.finditer(cleaned))
    return tables


def _checksum(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _list_migration_files(migrations_dir: Path, extension_id: str) -> list[Path]:
    if not migrations_dir.exists():
        return []
    files: list[Path] = []
    for entry in sorted(migrations_dir.iterdir()):
        if not entry.is_file() or entry.suffix != ".sql":
            continue
        if not _FILENAME_RE.fullmatch(entry.name):
            raise ExtensionMigrationError(
                f"invalid migration filename: {entry.name} "
                "(expected ^[0-9]{3,}_[a-z0-9_]+\\.sql$)",
                extension_id=extension_id,
            )
        files.append(entry)
    return files


def _table_prefix_for(extension_id: str) -> str:
    return "ext_" + extension_id.replace("-", "_") + "_"


def _validate_prefix(content: str, *, extension_id: str, filename: str) -> None:
    prefix = _table_prefix_for(extension_id)
    for table in _extract_table_targets(content):
        if not table.startswith(prefix):
            raise ExtensionMigrationError(
                f"{filename} targets table '{table}' outside the required prefix '{prefix}*'",
                extension_id=extension_id,
            )


def _already_applied(
    conn: sqlite3.Connection, *, extension_id: str, filename: str
) -> tuple[bool, str | None]:
    row = conn.execute(
        "SELECT checksum FROM _ext_migrations WHERE extension_id = ? AND filename = ?",
        (extension_id, filename),
    ).fetchone()
    if row is None:
        return False, None
    return True, row[0]


def _record_migration(
    conn: sqlite3.Connection,
    *,
    extension_id: str,
    filename: str,
    checksum: str,
) -> None:
    conn.execute(
        "INSERT INTO _ext_migrations (extension_id, filename, checksum, applied_at) "
        "VALUES (?, ?, ?, ?)",
        (extension_id, filename, checksum, _now()),
    )


def run_migrations(
    conn: sqlite3.Connection,
    *,
    extension_id: str,
    migrations_dir: Path,
) -> int:
    """Apply pending migrations for ``extension_id``.

    Returns the number of newly applied files. Idempotent: previously
    applied files are skipped silently as long as their checksum matches.

    Raises :class:`ExtensionMigrationError` if a file is malformed, a
    previously applied file has been edited, the SQL targets a table
    outside the extension's prefix, or SQL execution fails. The first
    failure aborts the entire run; no partial state is committed.
    """
    files = _list_migration_files(migrations_dir, extension_id)
    applied = 0
    for path in files:
        content = path.read_text(encoding="utf-8")
        checksum = _checksum(content)
        seen, recorded_checksum = _already_applied(
            conn, extension_id=extension_id, filename=path.name
        )
        if seen:
            if recorded_checksum != checksum:
                raise ExtensionMigrationError(
                    f"{path.name} has been edited since it was applied "
                    f"(recorded checksum {recorded_checksum[:8]}..., "
                    f"current checksum {checksum[:8]}...); never edit an "
                    "applied migration, add a new file instead",
                    extension_id=extension_id,
                )
            continue

        _validate_prefix(content, extension_id=extension_id, filename=path.name)

        statements = _split_statements(content)
        # SQLite implicitly commits any open transaction before DDL
        # statements when the Python sqlite3 module is in its default
        # deferred mode, so ``with conn:`` does not roll back partially
        # applied DDL. Wrap the migration in an explicit SAVEPOINT,
        # which DDL respects: a ROLLBACK TO + RELEASE undoes everything
        # done since the savepoint, including CREATE TABLE.
        savepoint = f"ext_migration_{extension_id.replace('-', '_')}"
        conn.execute(f"SAVEPOINT {savepoint}")
        try:
            for statement in statements:
                conn.execute(statement)
            _record_migration(
                conn,
                extension_id=extension_id,
                filename=path.name,
                checksum=checksum,
            )
        except sqlite3.Error as exc:
            conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
            conn.execute(f"RELEASE SAVEPOINT {savepoint}")
            raise ExtensionMigrationError(
                f"{path.name} failed to apply: {exc}",
                extension_id=extension_id,
            ) from exc
        else:
            conn.execute(f"RELEASE SAVEPOINT {savepoint}")
            conn.commit()

        applied += 1

    return applied


def table_prefix_for(extension_id: str) -> str:
    """Public helper: canonical table prefix for an extension id."""
    return _table_prefix_for(extension_id)
