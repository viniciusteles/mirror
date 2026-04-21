"""Build skill: DB-only context loader for Builder Mode."""

from __future__ import annotations

import argparse
import json
import sys

from memory.cli.conversation_logger import switch_conversation
from memory.client import MemoryClient
from memory.skills.mirror import _persist_global_sticky_defaults


def _print_builder_banner(slug: str, project_path: str | None = None) -> None:
    print(f"\033[38;5;117m⚙ Builder Mode active — journey: {slug}\033[0m", file=sys.stderr)
    if project_path:
        print(f"\033[38;5;117m  📁 {project_path}\033[0m", file=sys.stderr)


def _get_project_path(mem: MemoryClient, slug: str) -> str | None:
    row = mem.store.conn.execute(
        "SELECT metadata FROM identity WHERE layer = 'journey' AND key = ?", (slug,)
    ).fetchone()
    if row and row[0]:
        return json.loads(row[0]).get("project_path")
    return None


def _extract_query(journey_content: str, slug: str) -> str:
    lines = journey_content.splitlines()
    sections = ["description", "briefing", "context", "descrição", "contexto"]
    result = []
    capturing = False
    for line in lines:
        header = line.lstrip("#").strip().lower()
        if any(s in header for s in sections):
            capturing = True
            continue
        if capturing:
            if line.startswith("#"):
                break
            result.append(line)
    text = " ".join(result).strip()
    return text[:500] if text else slug


def cmd_load(slug: str) -> None:
    mem = MemoryClient()

    journey_content = mem.get_identity("journey", slug)
    if not journey_content:
        print(f"Error: journey '{slug}' not found.", file=sys.stderr)
        sys.exit(1)

    project_path = _get_project_path(mem, slug)
    _print_builder_banner(slug, project_path)

    context = mem.load_mirror_context(persona="engineer", journey=slug)
    print(context)

    raw_content = journey_content if isinstance(journey_content, str) else slug
    query_text = _extract_query(raw_content, slug)
    scoped = mem.search(query_text, limit=5, journey=slug)
    global_ = mem.search(query_text, limit=5)
    seen_ids: set[str] = set()
    merged: list = []
    for memory, score in scoped + global_:
        if memory.id not in seen_ids:
            seen_ids.add(memory.id)
            merged.append((memory, score))
    merged.sort(key=lambda x: x[1], reverse=True)
    relevant_memories = merged[:6]
    if relevant_memories:
        print("\n=== recent memories ===")
        for memory, _ in relevant_memories:
            print(f"\n[{memory.layer}] {memory.title}")
            print(memory.content)

    _persist_global_sticky_defaults(mem, persona="engineer", journey=slug)
    switch_conversation(persona="engineer", journey=slug)

    if project_path:
        print(f"\nproject_path={project_path}")
    else:
        print(
            f"\n[Journey '{slug}' has no project_path configured. "
            f"Run: python -m memory journey set-path {slug} /path/to/project]"
        )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build skill — DB context loader")
    sub = parser.add_subparsers(dest="command", required=True)

    p_load = sub.add_parser("load", help="Load journey context from DB (emits project_path)")
    p_load.add_argument("slug", help="Journey ID")

    args = parser.parse_args(argv)

    if args.command == "load":
        cmd_load(args.slug)
