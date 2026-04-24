"""Identity CLI: read and update identity directly in the database.

After the initial seed, identity is owned by the database — not the YAML files.
Use these commands to inspect and edit identity without touching any YAML.

Usage:
    python -m memory identity list [--layer LAYER] [--mirror-home PATH]
    python -m memory identity get <layer> <key> [--mirror-home PATH]
    python -m memory identity set <layer> <key> --content "..." [--mirror-home PATH]
    python -m memory identity edit <layer> <key> [--mirror-home PATH]
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from memory.cli.common import db_path_from_mirror_home
from memory.client import MemoryClient


def _client(mirror_home: str | None) -> MemoryClient:
    return MemoryClient(db_path=db_path_from_mirror_home(mirror_home))


def cmd_list(args: list[str]) -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="memory identity list",
        description="List identity entries stored in the database",
    )
    parser.add_argument("--layer", default=None, help="Filter by layer (e.g. ego, self, persona)")
    parser.add_argument("--mirror-home", default=None)
    parsed = parser.parse_args(args)

    mem = _client(parsed.mirror_home)

    if parsed.layer:
        entries = mem.store.get_identity_by_layer(parsed.layer)
    else:
        entries = mem.store.get_all_identity()

    if not entries:
        print("No identity entries found.")
        return

    current_layer = None
    for entry in entries:
        if entry.layer != current_layer:
            current_layer = entry.layer
            print(f"\n[{entry.layer}]")
        preview = entry.content[:70].replace("\n", " ")
        if len(entry.content) > 70:
            preview += "..."
        print(f"  {entry.key:<22}  {preview}")


def cmd_get(args: list[str]) -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="memory identity get",
        description="Print the content of one identity entry",
    )
    parser.add_argument("layer", help="Identity layer (e.g. ego, self, persona)")
    parser.add_argument("key", help="Identity key (e.g. behavior, soul, engineer)")
    parser.add_argument("--mirror-home", default=None)
    parsed = parser.parse_args(args)

    mem = _client(parsed.mirror_home)
    entry = mem.store.get_identity(parsed.layer, parsed.key)
    if not entry:
        print(f"No identity entry found for {parsed.layer}/{parsed.key}", file=sys.stderr)
        sys.exit(1)

    print(entry.content)


def cmd_set(args: list[str]) -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="memory identity set",
        description="Update identity content directly in the database",
    )
    parser.add_argument("layer", help="Identity layer (e.g. ego, self, persona)")
    parser.add_argument("key", help="Identity key (e.g. behavior, soul, engineer)")
    parser.add_argument(
        "--content",
        default=None,
        help="New content. If omitted, reads from stdin.",
    )
    parser.add_argument("--mirror-home", default=None)
    parsed = parser.parse_args(args)

    if parsed.content is not None:
        content = parsed.content
    else:
        content = sys.stdin.read()

    if not content.strip():
        print("Error: content is empty.", file=sys.stderr)
        sys.exit(1)

    mem = _client(parsed.mirror_home)
    existing = mem.store.get_identity(parsed.layer, parsed.key)
    mem.set_identity(parsed.layer, parsed.key, content)

    action = "updated" if existing else "created"
    print(f"✓ {parsed.layer}/{parsed.key} {action}")


def cmd_edit(args: list[str]) -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="memory identity edit",
        description="Edit identity content in $EDITOR and save directly to the database",
    )
    parser.add_argument("layer", help="Identity layer (e.g. ego, self, persona)")
    parser.add_argument("key", help="Identity key (e.g. behavior, soul, engineer)")
    parser.add_argument("--mirror-home", default=None)
    parsed = parser.parse_args(args)

    mem = _client(parsed.mirror_home)
    existing = mem.store.get_identity(parsed.layer, parsed.key)
    current_content = existing.content if existing else ""

    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL") or "nano"

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".md",
        prefix=f"mirror-identity-{parsed.layer}-{parsed.key}-",
        delete=False,
        encoding="utf-8",
    ) as f:
        f.write(current_content)
        tmp_path = Path(f.name)

    try:
        result = subprocess.run([editor, str(tmp_path)])
        if result.returncode != 0:
            print(f"Editor exited with code {result.returncode}. Aborted.", file=sys.stderr)
            sys.exit(1)

        new_content = tmp_path.read_text(encoding="utf-8")
    finally:
        tmp_path.unlink(missing_ok=True)

    if not new_content.strip():
        print("Content is empty after editing. No changes saved.", file=sys.stderr)
        sys.exit(1)

    if new_content == current_content:
        print("No changes detected.")
        return

    mem.set_identity(parsed.layer, parsed.key, new_content)
    action = "updated" if existing else "created"
    print(f"✓ {parsed.layer}/{parsed.key} {action}")


_SUBCOMMANDS = {
    "list": cmd_list,
    "get": cmd_get,
    "set": cmd_set,
    "edit": cmd_edit,
}

_USAGE = """\
Usage: python -m memory identity <subcommand> [args]

Subcommands:
  list [--layer LAYER]               List all identity entries in the database
  get  <layer> <key>                 Print content of one identity entry
  set  <layer> <key> --content STR   Update content (reads stdin if --content omitted)
  edit <layer> <key>                 Open entry in $EDITOR and save to the database

Examples:
  python -m memory identity list
  python -m memory identity list --layer ego
  python -m memory identity get ego behavior
  python -m memory identity edit self soul
  python -m memory identity set user identity --content "# About me\\n..."
  echo "new content" | python -m memory identity set ego behavior
"""


def main(args: list[str] | None = None) -> None:
    if args is None:
        args = sys.argv[1:]

    if not args or args[0] not in _SUBCOMMANDS:
        print(_USAGE)
        sys.exit(0 if not args else 1)

    _SUBCOMMANDS[args[0]](args[1:])


if __name__ == "__main__":
    main()
