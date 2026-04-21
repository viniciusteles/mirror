"""Record a journal entry in the memory database."""

import argparse
import json
import sys

from memory import MemoryClient
from memory.cli.common import db_path_from_mirror_home


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Record a journal entry")
    parser.add_argument("--journey", help="Journey slug")
    parser.add_argument(
        "--mirror-home",
        default=None,
        help="Explicit user home whose database should be used for this command",
    )
    parser.add_argument("content", nargs="+", help="Journal entry text")
    args = parser.parse_args(argv)

    content = " ".join(args.content)
    if not content.strip():
        print("Error: journal entry text cannot be empty", file=sys.stderr)
        sys.exit(1)

    mem = MemoryClient(db_path=db_path_from_mirror_home(args.mirror_home))
    memory = mem.add_journal(content=content, journey=args.journey)

    tags: list[str] = []
    if memory.tags:
        try:
            tags = json.loads(memory.tags)
        except (json.JSONDecodeError, TypeError):
            pass

    layer_labels = {
        "self": "Self (identity)",
        "ego": "Ego (operational)",
        "shadow": "Shadow (tension)",
    }
    layer_label = layer_labels.get(memory.layer, memory.layer)

    print("📓 Journal entry recorded")
    print(f"   Title: {memory.title}")
    print(f"   Layer: {layer_label}")
    print(f"   Tags: {', '.join(tags)}")
    if args.journey:
        print(f"   Journey: {args.journey}")
    print(f"   ID: {memory.id[:8]}")


if __name__ == "__main__":
    main()
