"""Journey CLI: inspect and update journey status."""

import argparse
import sys

from memory import MemoryClient
from memory.cli.common import db_path_from_mirror_home


def cmd_status(journey: str | None, *, mirror_home: str | None = None) -> None:
    mem = MemoryClient(db_path=db_path_from_mirror_home(mirror_home))
    status = mem.get_journey_status(journey)

    for name, data in status.items():
        print(f"=== journey: {name} ===")

        if data.get("identity"):
            print("\n--- identity ---")
            print(data["identity"])

        if data.get("journey_path"):
            print("\n--- journey path ---")
            print(data["journey_path"])

        memories = data.get("recent_memories", [])
        if memories:
            print(f"\n--- recent memories ({len(memories)}) ---")
            for m in memories:
                print(f"  [{m.created_at[:10]}] {m.title}")
        else:
            print("\n--- recent memories ---")
            print("  No recent memories.")

        conversations = data.get("recent_conversations", [])
        if conversations:
            print(f"\n--- recent conversations ({len(conversations)}) ---")
            for c in conversations:
                title = c.title or "(untitled)"
                print(f"  [{c.started_at[:10]}] {title}")
        else:
            print("\n--- recent conversations ---")
            print("  No recent conversations.")

        print()


def cmd_set_path(journey: str, path: str, *, mirror_home: str | None = None) -> None:
    from pathlib import Path

    mem = MemoryClient(db_path=db_path_from_mirror_home(mirror_home))
    if not mem.get_identity("journey", journey):
        print(f"Error: journey '{journey}' not found.", file=sys.stderr)
        sys.exit(1)
    row = mem.store.conn.execute(
        "SELECT metadata FROM identity WHERE layer = 'journey' AND key = ?", (journey,)
    ).fetchone()
    import json

    meta = json.loads(row[0]) if row and row[0] else {}
    meta["project_path"] = str(Path(path).expanduser().resolve())
    mem.store.conn.execute(
        "UPDATE identity SET metadata = ? WHERE layer = 'journey' AND key = ?",
        (json.dumps(meta), journey),
    )
    mem.store.conn.commit()
    print(f"project_path set for '{journey}': {meta['project_path']}", file=sys.stderr)
    print(meta["project_path"])


def cmd_update(journey: str, content: str, *, mirror_home: str | None = None) -> None:
    if content == "-":
        content = sys.stdin.read()
    mem = MemoryClient(db_path=db_path_from_mirror_home(mirror_home))
    mem.set_journey_path(journey, content)
    print(f"Journey path '{journey}' updated.", file=sys.stderr)


def _parse_args(argv: list[str]) -> tuple[str | None, list[str]]:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--mirror-home", default=None)
    parsed, remaining = parser.parse_known_args(argv)
    return parsed.mirror_home, remaining


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    mirror_home, remaining = _parse_args(args)

    if remaining and remaining[0] == "update":
        if len(remaining) < 3:
            print("Usage: python -m memory journey update <slug> <content|-stdin>", file=sys.stderr)
            sys.exit(1)
        cmd_update(remaining[1], remaining[2], mirror_home=mirror_home)
    elif remaining and remaining[0] == "set-path":
        if len(remaining) < 3:
            print("Usage: python -m memory journey set-path <slug> <path>", file=sys.stderr)
            sys.exit(1)
        cmd_set_path(remaining[1], remaining[2], mirror_home=mirror_home)
    else:
        # Optional: journey status [slug]
        slug = (
            remaining[1]
            if len(remaining) >= 2 and remaining[0] == "status"
            else (remaining[0] if remaining else None)
        )
        cmd_status(slug, mirror_home=mirror_home)


if __name__ == "__main__":
    main()
