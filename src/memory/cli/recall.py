"""Load messages from a previous conversation."""

import argparse
import sys

from memory import MemoryClient
from memory.cli.common import db_path_from_mirror_home
from memory.models import Conversation


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Load a previous conversation")
    parser.add_argument("conv_id", help="Conversation ID (full or prefix)")
    parser.add_argument("--limit", type=int, default=50, help="Maximum number of messages")
    parser.add_argument(
        "--mirror-home",
        default=None,
        help="Explicit user home whose database should be read for this command",
    )
    args = parser.parse_args(argv)

    mem = MemoryClient(db_path=db_path_from_mirror_home(args.mirror_home))

    row = mem.store.conn.execute(
        "SELECT * FROM conversations WHERE id LIKE ? ORDER BY started_at DESC LIMIT 1",
        (f"{args.conv_id}%",),
    ).fetchone()

    if not row:
        print(f"Conversation '{args.conv_id}' not found.", file=sys.stderr)
        sys.exit(1)

    conv = Conversation(**dict(row))

    print(f"# Conversation: {conv.title or '(untitled)'}")
    print(f"**Date:** {conv.started_at[:10] if conv.started_at else '?'}")
    if conv.persona:
        print(f"**Persona:** {conv.persona}")
    if conv.journey:
        print(f"**Journey:** {conv.journey}")
    print(f"**ID:** `{conv.id}`")
    print()
    print("---")
    print()

    messages = mem.store.get_messages(conv.id)
    if not messages:
        print("(conversation has no messages)")
        return

    for msg in messages[-args.limit :]:
        role_label = "**User:**" if msg.role == "user" else "**Mirror:**"
        print(role_label)
        print(msg.content)
        print()


if __name__ == "__main__":
    main()
