"""CLI: render the state-aware welcome card.

See docs/product/specs/welcome/index.md for the contract. The welcome is
designed to be cheap (SQLite reads only, no network) so a runtime can call
it at every session_start without latency cost.
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

from memory import MemoryClient
from memory.cli.common import db_path_from_mirror_home
from memory.config import resolve_mirror_home

INVITATION = "→ Where shall we begin?"
SEPARATOR = " · "

_MONTH_ABBR = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)


# --------- public entry point --------------------------------------------


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Render the state-aware welcome card",
    )
    parser.add_argument(
        "--mirror-home",
        default=None,
        help="Explicit user home whose database should be read for the welcome",
    )
    args = parser.parse_args(argv)

    if _welcome_disabled():
        return

    welcome = compose_welcome(mirror_home=args.mirror_home)
    if welcome:
        print(welcome)


# --------- composition ---------------------------------------------------


def compose_welcome(mirror_home: str | Path | None = None) -> str:
    """Compose the welcome string. Returns "" when no header can be rendered.

    The only path to empty output is an unresolvable Mirror home. A fresh
    database with zero memories, zero journeys, etc. still renders the full
    welcome with zeroes.
    """
    home_path = _resolve_home(mirror_home)
    if home_path is None:
        return ""

    db_path = db_path_from_mirror_home(home_path)
    stats_line = _stats_line(db_path)
    return _render(user=home_path.name, stats=stats_line)


# --------- renderers -----------------------------------------------------


def _render(user: str, stats: str) -> str:
    return "\n".join(
        [
            f"◇ Mirror · {user}",
            stats,
            "",
            INVITATION,
        ]
    )


def _stats_line(db_path: Path | None) -> str:
    if db_path is None or not db_path.exists():
        return _format_stats(journeys=0, personas=0, memories=0, conversations=0, since=None)

    with MemoryClient(db_path=db_path) as mem:
        journeys = len(mem.list_active_journeys())
        personas = _count_identity_rows(mem, layer="persona")
        memories = _scalar(mem, "SELECT COUNT(*) FROM memories")
        conversations = _scalar(mem, "SELECT COUNT(*) FROM conversations")
        first_started = _scalar(mem, "SELECT MIN(started_at) FROM conversations")

    return _format_stats(
        journeys=journeys,
        personas=personas,
        memories=memories,
        conversations=conversations,
        since=first_started,
    )


def _format_stats(
    *,
    journeys: int,
    personas: int,
    memories: int,
    conversations: int,
    since: str | None,
) -> str:
    parts = [
        f"{_fmt_count(journeys)} journeys",
        f"{_fmt_count(personas)} personas",
        f"{_fmt_count(memories)} memories",
        f"{_fmt_count(conversations)} conversations",
        _since_label(since),
    ]
    return SEPARATOR.join(parts)


# --------- helpers -------------------------------------------------------


def _count_identity_rows(mem: MemoryClient, *, layer: str) -> int:
    return _scalar(
        mem,
        "SELECT COUNT(*) FROM identity WHERE layer = ?",
        (layer,),
    )


def _scalar(mem: MemoryClient, sql: str, params: tuple = ()) -> int:
    row = mem.store.conn.execute(sql, params).fetchone()
    if row is None:
        return 0
    value = row[0]
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return value  # type: ignore[return-value]
    return int(value)


def _fmt_count(value: int) -> str:
    if value >= 1000:
        return f"{value:,}"
    return str(value)


def _since_label(first_started: str | None) -> str:
    if not first_started:
        return "since today"
    dt = _parse_iso(first_started)
    if dt is None:
        return "since today"
    month = _MONTH_ABBR[dt.month - 1]
    return f"since {month} {dt.year}"


def _resolve_home(mirror_home: str | Path | None) -> Path | None:
    try:
        return resolve_mirror_home(mirror_home=mirror_home)
    except ValueError:
        return None


def _welcome_disabled() -> bool:
    value = os.environ.get("MIRROR_WELCOME", "").strip().lower()
    return value in {"off", "0", "false", "no"}


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


# The timezone import is kept available for callers that mock _iso_now in
# future. Currently the welcome reads stored ISO timestamps and does not
# compute relative time itself.
_ = timezone


if __name__ == "__main__":
    main()
