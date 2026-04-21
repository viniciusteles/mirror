"""CLI: list journeys with status, stage, and description."""

import argparse
import re

from memory import MemoryClient
from memory.cli.common import db_path_from_mirror_home


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="List journeys with status and stage")
    parser.add_argument(
        "--mirror-home",
        default=None,
        help="Explicit user home whose database should be read for this command",
    )
    args = parser.parse_args(argv)

    mem = MemoryClient(db_path=db_path_from_mirror_home(args.mirror_home))
    journeys = mem.store.get_identity_by_layer("journey")

    if not journeys:
        print("No journeys found.")
        return

    for t in journeys:
        name = t.key
        content = t.content or ""

        status_match = re.search(r"\*\*Status:\*\*\s*(.+)", content)
        status = status_match.group(1).strip() if status_match else "?"

        desc = ""
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith(("## Description", "## Descrição")):
                continue
            if line and not line.startswith("#") and not line.startswith("**"):
                desc = line[:80]
                break

        journey_path_raw = mem.get_identity("journey_path", name)
        journey_path = journey_path_raw if isinstance(journey_path_raw, str) else ""
        stage_match = re.search(r"\*\*(?:Current stage|Etapa atual):\*\*\s*(.+)", journey_path)
        stage = stage_match.group(1).strip() if stage_match else "—"

        icon = {"active": "🚧", "completed": "✅", "paused": "⏸"}.get(status, "•")
        print(f"{icon} **{name}** ({status})")
        print(f"  Stage: {stage}")
        if desc:
            print(f"  {desc}")
        print()


if __name__ == "__main__":
    main()
