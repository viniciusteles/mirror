"""Backup and cleanup for the configured memory database."""

import argparse
import sys
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

RETENTION_DAYS = 30


def _default_paths() -> tuple[Path, Path]:
    from memory.config import DB_BACKUP_PATH, DB_PATH

    return DB_PATH, DB_BACKUP_PATH


def backup(
    silent: bool = False,
    db_path: Path | None = None,
    db_backup_path: Path | None = None,
    mirror_home: Path | None = None,
) -> Path | None:
    """Create a zipped backup of the configured database and remove old backups.

    Returns:
        Created backup path, or None when the database does not exist.
    """
    if db_path is None and db_backup_path is None and mirror_home is not None:
        import os

        db_path = mirror_home / "memory.db"
        if os.environ.get("BACKUP_DIR"):
            from memory.config import BACKUP_DIR

            db_backup_path = BACKUP_DIR
        else:
            db_backup_path = mirror_home / "backups"
    elif db_path is None or db_backup_path is None:
        default_db_path, default_db_backup_path = _default_paths()
        if db_path is None:
            db_path = default_db_path
        if db_backup_path is None:
            db_backup_path = default_db_backup_path

    if not silent:
        if mirror_home is not None:
            print(f"Mirror home: {mirror_home}")
        print(f"Database: {db_path}")
        print(f"Backup dir: {db_backup_path}")

    if not db_path.exists():
        if not silent:
            print(f"Database not found: {db_path}")
        return None

    db_backup_path.mkdir(parents=True, exist_ok=True)

    # Create backup.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_backup_path / f"memory_{timestamp}.zip"

    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(db_path, "memory.db")
        # Include WAL and SHM sidecars when present for SQLite consistency.
        for suffix in ("-wal", "-shm"):
            wal = db_path.parent / f"{db_path.name}{suffix}"
            if wal.exists():
                zf.write(wal, f"memory.db{suffix}")

    if not silent:
        size_kb = backup_path.stat().st_size / 1024
        print(f"Backup created: {backup_path.name} ({size_kb:.0f} KB)")

    # Clean up old backups.
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    removed = 0
    for old in db_backup_path.glob("memory_*.zip"):
        if old == backup_path:
            continue
        try:
            # Extract date from name: memory_YYYYMMDD_HHMMSS.zip.
            date_str = old.stem.replace("memory_", "")
            file_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
            if file_date < cutoff:
                old.unlink()
                removed += 1
        except (ValueError, OSError):
            continue

    if not silent and removed > 0:
        print(f"Removed {removed} backup(s) older than {RETENTION_DAYS} days.")

    return backup_path


def main():
    """Command-line entry point."""
    from memory.config import _RESOLVED_MIRROR_HOME

    parser = argparse.ArgumentParser(description="Create a zipped backup of the memory database")
    parser.add_argument("--silent", action="store_true")
    parser.add_argument(
        "--mirror-home",
        default=None,
        help="Explicit user home to back up; overrides MIRROR_HOME-derived defaults for this command",
    )
    args = parser.parse_args()

    mirror_home = Path(args.mirror_home).expanduser() if args.mirror_home else _RESOLVED_MIRROR_HOME
    result = backup(silent=args.silent, mirror_home=mirror_home)
    if result is None and not args.silent:
        sys.exit(1)


if __name__ == "__main__":
    main()
