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

    summaries = mem.conversations.list_recent(
        limit=args.limit,
        journey=args.journey,
        persona=args.persona,
    )

    if not summaries:
        print("No conversations found.")
        return

    for summary in summaries:
        title = summary.title or "(untitled)"
        date = summary.started_at[:10] if summary.started_at else "?"
        persona_str = f" ◇ {summary.persona}" if summary.persona else ""
        journey_str = f" [{summary.journey}]" if summary.journey else ""
        print(
            f"**{date}** | `{summary.id[:8]}`{journey_str}{persona_str} "
            f"({summary.message_count} msgs)"
        )
        print(f"  {title}")
        print()


if __name__ == "__main__":
    main()
