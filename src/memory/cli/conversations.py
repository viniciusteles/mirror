"""List recent conversations from the memory database."""

import argparse

from memory import MemoryClient
from memory.cli.common import db_path_from_mirror_home


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="List recent conversations")
    parser.add_argument("--limit", type=int, default=20, help="Number of conversations")
    parser.add_argument("--journey", help="Filter by journey")
    parser.add_argument("--persona", help="Filter by persona")
    parser.add_argument(
        "--mirror-home",
        default=None,
        help="Explicit user home whose database should be read for this command",
    )
    args = parser.parse_args(argv)

    mem = MemoryClient(db_path=db_path_from_mirror_home(args.mirror_home))

    conditions = ["1=1"]
    params: list[str | int] = []

    if args.journey:
        conditions.append("journey = ?")
        params.append(args.journey)
    if args.persona:
        conditions.append("persona = ?")
        params.append(args.persona)

    where = " AND ".join(conditions)
    params.append(args.limit)

    rows = mem.store.conn.execute(
        f"""SELECT id, title, started_at, persona, journey,
                   (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as msg_count
            FROM conversations c
            WHERE {where}
            ORDER BY started_at DESC
            LIMIT ?""",
        params,
    ).fetchall()

    if not rows:
        print("No conversations found.")
        return

    for conv_id, title, started_at, persona, journey, msg_count in rows:
        title = title or "(untitled)"
        date = started_at[:10] if started_at else "?"
        persona_str = f" ◇ {persona}" if persona else ""
        journey_str = f" [{journey}]" if journey else ""
        print(f"**{date}** | `{conv_id[:8]}`{journey_str}{persona_str} ({msg_count} msgs)")
        print(f"  {title}")
        print()


if __name__ == "__main__":
    main()
