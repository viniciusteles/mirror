"""Weekly planning: view the current week or ingest a free-text plan."""

import argparse
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from memory import MemoryClient
from memory.cli.common import db_path_from_mirror_home

WEEKDAYS_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
PENDING_FILE = Path(tempfile.gettempdir()) / "mm_week_pending.json"


def cmd_view(mem: MemoryClient) -> None:
    now = datetime.now()
    today = now.date()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)

    tasks = mem.store.get_tasks_for_week(start.isoformat(), end.isoformat())

    if not tasks:
        print("No items in the current week.")
        return

    visible = []
    for t in tasks:
        if t.scheduled_at and t.status != "done":
            try:
                sched = datetime.fromisoformat(t.scheduled_at)
                if sched < now:
                    continue
            except ValueError:
                pass
        visible.append(t)

    if not visible:
        print("No pending items in the current week.")
        return

    by_day: dict[str, list] = {}
    for t in visible:
        day = t.due_date or (t.scheduled_at[:10] if t.scheduled_at else None)
        if day:
            by_day.setdefault(day, []).append(t)

    for day in by_day:
        by_day[day].sort(key=lambda t: (t.scheduled_at or "99", t.time_hint or "zz", t.title))

    week_label = f"{start.strftime('%d/%m')}-{end.strftime('%d/%m/%Y')}"
    print(f"📅 Week {week_label}\n")

    for day_offset in range(7):
        day = (start + timedelta(days=day_offset)).isoformat()
        if day not in by_day:
            continue

        day_date = start + timedelta(days=day_offset)
        wd = WEEKDAYS_FULL[day_date.weekday()]
        marker = " (today)" if day_date == today else ""
        print(f"━━ {wd} {day_date.strftime('%d/%m')}{marker} ━━")

        for t in by_day[day]:
            icon = (
                "📌"
                if t.scheduled_at
                else "✅"
                if t.status == "done"
                else "◐"
                if t.status == "doing"
                else "✖"
                if t.status == "blocked"
                else "🔧"
            )
            if t.scheduled_at:
                try:
                    time_str = datetime.fromisoformat(t.scheduled_at).strftime("%H:%M")
                except ValueError:
                    time_str = ""
            elif t.time_hint:
                time_str = t.time_hint
            else:
                time_str = ""

            overdue = (
                " ⚠ overdue"
                if not t.scheduled_at
                and t.due_date
                and t.due_date < today.isoformat()
                and t.status not in ("done",)
                else ""
            )
            journey = f"  [{t.journey}]" if t.journey else ""
            time_col = f"{time_str:>20}" if time_str else " " * 20
            print(f"  {icon} {t.title:<40}{time_col}{journey}{overdue}")

        print()


def cmd_plan(mem: MemoryClient, text: str) -> None:
    items = mem.ingest_week_plan(text)
    if not items:
        print("No temporal items found in the text.")
        return

    pending = []
    output = {"items": [], "pending_file": str(PENDING_FILE)}

    for entry in items:
        item = entry["item"]
        payload = {
            "title": item.title,
            "due_date": item.due_date,
            "scheduled_at": item.scheduled_at,
            "time_hint": item.time_hint,
            "journey": item.journey,
            "context": item.context,
        }
        pending.append(payload)
        item_out = dict(payload)
        similar = entry.get("similar_existing", [])
        if similar:
            item_out["warning"] = f"Similar item already exists: '{similar[0].title}'"
        output["items"].append(item_out)

    PENDING_FILE.write_text(json.dumps(pending, ensure_ascii=False, indent=2))
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_save(mem: MemoryClient) -> None:
    if not PENDING_FILE.exists():
        print("No pending items to save.")
        return

    from memory.models import ExtractedWeekItem

    pending = json.loads(PENDING_FILE.read_text())
    items = [ExtractedWeekItem(**p) for p in pending]
    created = mem.save_week_items(items)
    PENDING_FILE.unlink(missing_ok=True)

    print(f"✅ {len(created)} items saved:")
    for t in created:
        time_str = ""
        if t.scheduled_at:
            try:
                time_str = f" at {datetime.fromisoformat(t.scheduled_at).strftime('%H:%M')}"
            except ValueError:
                pass
        elif t.time_hint:
            time_str = f" ({t.time_hint})"
        journey = f" [{t.journey}]" if t.journey else ""
        print(f"  ○ `{t.id}` {t.title} - {t.due_date}{time_str}{journey}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Weekly planning")
    parser.add_argument(
        "--mirror-home",
        default=None,
        help="Explicit user home whose database should be used for this command",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("view")
    p_plan = subparsers.add_parser("plan")
    p_plan.add_argument("text", help="Free text with the weekly plan")
    subparsers.add_parser("save")

    args = parser.parse_args(argv)
    mem = MemoryClient(db_path=db_path_from_mirror_home(args.mirror_home))

    if args.command == "plan":
        cmd_plan(mem, args.text)
    elif args.command == "save":
        cmd_save(mem)
    else:
        cmd_view(mem)


if __name__ == "__main__":
    main()
