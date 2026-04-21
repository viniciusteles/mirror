"""List memories with filters by type, layer, and journey."""

import argparse
import json

from memory import MemoryClient
from memory.cli.common import db_path_from_mirror_home

ICONS = {
    "decision": "⚖️",
    "insight": "💡",
    "idea": "🌱",
    "journal": "📓",
    "tension": "⚡",
    "learning": "📚",
    "pattern": "🔄",
    "commitment": "🤝",
    "reflection": "🪞",
}


def _print_memory_row(row: tuple) -> None:  # type: ignore[type-arg]
    mem_id, mem_type, layer, title, content, _context, journey, persona, tags, created_at = row
    icon = ICONS.get(mem_type, "•")
    date = created_at[:10] if created_at else "?"
    journey_str = f" 🧭 {journey}" if journey else ""
    persona_str = f" ◇ {persona}" if persona else ""

    tags_list: list[str] = []
    if tags:
        try:
            tags_list = json.loads(tags)
        except (json.JSONDecodeError, TypeError):
            pass
    tags_str = f"  🏷 {', '.join(tags_list)}" if tags_list else ""

    print(f"{icon} **{title}**")
    print(f"  {date} | `{mem_id[:8]}` | {mem_type} [{layer}]{journey_str}{persona_str}")
    print(f"  {content[:200]}")
    if tags_str:
        print(tags_str)
    print()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="List memories from the memory database")
    parser.add_argument("--type", dest="memory_type", help="Filter by type")
    parser.add_argument("--layer", help="Filter by layer (self/ego/shadow)")
    parser.add_argument("--journey", help="Filter by journey")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number")
    parser.add_argument("--search", help="Semantic search query")
    parser.add_argument(
        "--mirror-home",
        default=None,
        help="Explicit user home whose database should be read for this command",
    )
    args = parser.parse_args(argv)

    mem = MemoryClient(db_path=db_path_from_mirror_home(args.mirror_home))

    if args.search:
        results = mem.search(
            args.search,
            limit=args.limit,
            memory_type=args.memory_type,
            layer=args.layer,
            journey=args.journey,
        )
        if not results:
            print("No memories found.")
            return

        print(f'🔍 Search: "{args.search}" ({len(results)} results)\n')
        for memory, score in results:
            icon = ICONS.get(memory.memory_type, "•")
            date = memory.created_at[:10] if memory.created_at else "?"
            journey_str = f" 🧭 {memory.journey}" if memory.journey else ""
            tags_list: list[str] = []
            if memory.tags:
                try:
                    tags_list = (
                        json.loads(memory.tags) if isinstance(memory.tags, str) else memory.tags
                    )
                except (json.JSONDecodeError, TypeError):
                    pass
            tags_str = f"  🏷 {', '.join(tags_list)}" if tags_list else ""
            print(f"{icon} **{memory.title}** (score: {score:.3f})")
            print(
                f"  {date} | `{memory.id[:8]}` | {memory.memory_type} [{memory.layer}]{journey_str}"
            )
            print(f"  {memory.content[:200]}")
            if tags_str:
                print(tags_str)
            print()
        return

    conditions = ["1=1"]
    params: list[str | int] = []
    if args.memory_type:
        conditions.append("memory_type = ?")
        params.append(args.memory_type)
    if args.layer:
        conditions.append("layer = ?")
        params.append(args.layer)
    if args.journey:
        conditions.append("journey = ?")
        params.append(args.journey)

    where = " AND ".join(conditions)
    params.append(args.limit)

    rows = mem.store.conn.execute(
        f"""SELECT id, memory_type, layer, title, content, context,
                   journey, persona, tags, created_at
            FROM memories
            WHERE {where}
            ORDER BY created_at DESC
            LIMIT ?""",
        params,
    ).fetchall()

    if not rows:
        print("No memories found.")
        return

    filter_parts = []
    if args.memory_type:
        filter_parts.append(f"type={args.memory_type}")
    if args.layer:
        filter_parts.append(f"layer={args.layer}")
    if args.journey:
        filter_parts.append(f"journey={args.journey}")
    filter_str = f" ({', '.join(filter_parts)})" if filter_parts else ""

    type_counts = mem.store.conn.execute(
        "SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type"
    ).fetchall()
    totals = " | ".join(
        f"{ICONS.get(t, '•')} {t}: {c}" for t, c in sorted(type_counts, key=lambda r: r[0])
    )
    print(f"📦 Memories{filter_str} — {len(rows)} shown\n{totals}\n")

    for row in rows:
        _print_memory_row(row)


if __name__ == "__main__":
    main()
