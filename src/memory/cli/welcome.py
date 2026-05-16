"""CLI: render the state-aware welcome card.

See docs/product/specs/welcome/index.md for the contract. The welcome is
designed to be cheap (SQLite reads only, no network) so a runtime can call
it at every session_start without latency cost.
"""

from __future__ import annotations

import argparse
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from memory import MemoryClient
from memory.cli.common import db_path_from_mirror_home
from memory.config import resolve_mirror_home

INVITATION = "→ Where shall we begin?"

_STAGE_PATTERN = re.compile(
    r"\*\*(?:Current stage|Etapa atual|Fase)[^*]*:\*\*\s*(.+)", re.IGNORECASE
)
_NEXT_PATTERN = re.compile(
    r"\*\*(?:Next action|Next|Próxima ação|Próximo)[^*]*:\*\*\s*(.+)", re.IGNORECASE
)

_INSIGHT_LAYERS = ("self", "ego")
_INSIGHT_WINDOW = timedelta(days=30)
_CONVERSATION_WINDOW = timedelta(hours=48)


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
    """Compose the welcome string. Returns "" when nothing should render.

    This function is the contract. Runtimes that want the welcome go through
    `main()` (which adds env-var handling). Tests target both.
    """
    home_path = _resolve_home(mirror_home)
    if home_path is None:
        return ""

    db_path = db_path_from_mirror_home(home_path)
    if db_path is None or not Path(db_path).exists():
        return _render(user=home_path.name, journey_line=None, context_line=None)

    with MemoryClient(db_path=db_path) as mem:
        active = _pick_active_journey(mem)
        journey_line = _journey_line(mem, active) if active else None
        context_line = _context_line(mem, active) if active else None
        return _render(home_path.name, journey_line, context_line)


# --------- renderers -----------------------------------------------------


def _render(user: str, journey_line: str | None, context_line: str | None) -> str:
    lines: list[str] = [f"◇ Mirror · {user}"]
    if journey_line:
        lines.append(journey_line)
    if context_line:
        lines.append(context_line)
    lines.append("")
    lines.append(INVITATION)
    return "\n".join(lines)


def _journey_line(mem: MemoryClient, journey: str) -> str:
    journey_path = mem.get_journey_path(journey) or ""
    stage = _first_match(_STAGE_PATTERN, journey_path)
    next_action = _first_match(_NEXT_PATTERN, journey_path)

    parts: list[str] = [f"Active journey: {journey}"]
    if stage:
        parts[-1] = f"{parts[-1]} — {stage}"
    if next_action:
        parts.append(f"next: {next_action}")
    return " · ".join(parts)


def _context_line(mem: MemoryClient, journey: str) -> str | None:
    insight = _last_insight(mem, journey)
    if insight:
        return f'Last insight: "{insight}"'
    recent_conv = _recent_conversation(mem, journey)
    if recent_conv:
        hours, title = recent_conv
        return f"Last conversation {hours}h ago — {title}"
    return None


# --------- selection rules -----------------------------------------------


def _pick_active_journey(mem: MemoryClient) -> str | None:
    """Return the journey id the mirror is currently engaged with, or None."""
    active = {j["id"] for j in mem.list_active_journeys()}
    if not active:
        return None

    # 1. Journey of the most recent conversation across all active journeys.
    for j in _journeys_by_recent_conversation(mem, active):
        return j

    # 2. Journey of the most recent memory across all active journeys.
    for j in _journeys_by_recent_memory(mem, active):
        return j

    # 3. Fallback: first active journey as returned by list_active_journeys().
    for j_dict in mem.list_active_journeys():
        if j_dict["id"] in active:
            return j_dict["id"]
    return None


def _journeys_by_recent_conversation(mem: MemoryClient, candidates: set[str]):
    rows = mem.store.conn.execute(
        """SELECT journey FROM conversations
           WHERE journey IS NOT NULL
           ORDER BY COALESCE(ended_at, started_at) DESC"""
    ).fetchall()
    seen: set[str] = set()
    for row in rows:
        j = row["journey"] if hasattr(row, "keys") else row[0]
        if j in candidates and j not in seen:
            seen.add(j)
            yield j


def _journeys_by_recent_memory(mem: MemoryClient, candidates: set[str]):
    rows = mem.store.conn.execute(
        """SELECT journey FROM memories
           WHERE journey IS NOT NULL
           ORDER BY created_at DESC"""
    ).fetchall()
    seen: set[str] = set()
    for row in rows:
        j = row["journey"] if hasattr(row, "keys") else row[0]
        if j in candidates and j not in seen:
            seen.add(j)
            yield j


def _last_insight(mem: MemoryClient, journey: str) -> str | None:
    cutoff = _iso_now() - _INSIGHT_WINDOW
    placeholders = ",".join(["?"] * len(_INSIGHT_LAYERS))
    row = mem.store.conn.execute(
        f"""SELECT title, created_at FROM memories
            WHERE journey = ?
              AND layer IN ({placeholders})
            ORDER BY created_at DESC
            LIMIT 1""",
        (journey, *_INSIGHT_LAYERS),
    ).fetchone()
    if not row:
        return None
    title = row["title"] if hasattr(row, "keys") else row[0]
    created_at = row["created_at"] if hasattr(row, "keys") else row[1]
    if not title:
        return None
    created_dt = _parse_iso(created_at)
    if created_dt and created_dt < cutoff:
        return None
    return str(title).strip()


def _recent_conversation(mem: MemoryClient, journey: str) -> tuple[int, str] | None:
    cutoff = _iso_now() - _CONVERSATION_WINDOW
    row = mem.store.conn.execute(
        """SELECT title, summary, ended_at FROM conversations
           WHERE journey = ?
             AND ended_at IS NOT NULL
           ORDER BY ended_at DESC
           LIMIT 1""",
        (journey,),
    ).fetchone()
    if not row:
        return None
    ended_at = row["ended_at"] if hasattr(row, "keys") else row[2]
    ended_dt = _parse_iso(ended_at)
    if not ended_dt or ended_dt < cutoff:
        return None
    hours = max(1, int((_iso_now() - ended_dt).total_seconds() // 3600))
    title = (row["title"] if hasattr(row, "keys") else row[0]) or (
        row["summary"] if hasattr(row, "keys") else row[1]
    )
    if not title:
        title = "untitled"
    return hours, str(title).strip()


# --------- helpers -------------------------------------------------------


def _resolve_home(mirror_home: str | Path | None) -> Path | None:
    try:
        return resolve_mirror_home(mirror_home=mirror_home)
    except ValueError:
        return None


def _welcome_disabled() -> bool:
    value = os.environ.get("MIRROR_WELCOME", "").strip().lower()
    return value in {"off", "0", "false", "no"}


def _first_match(pattern: re.Pattern[str], text: str) -> str | None:
    m = pattern.search(text or "")
    if not m:
        return None
    value = m.group(1).strip()
    return value or None


def _iso_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        # Python's fromisoformat handles "...+00:00"; some rows store "Z".
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


if __name__ == "__main__":
    main()
