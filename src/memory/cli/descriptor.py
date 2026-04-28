"""Generate and list routing descriptors for personas and journeys."""

from __future__ import annotations

import argparse
import sys

from memory import MemoryClient
from memory.cli.common import db_path_from_mirror_home
from memory.intelligence.extraction import generate_descriptor


def _cmd_generate(args: argparse.Namespace) -> None:
    mem = MemoryClient(db_path=db_path_from_mirror_home(args.mirror_home))

    # Collect entities to describe.
    targets: list[tuple[str, str, str]] = []  # (layer, key, content)

    if args.layer and args.key:
        # Specific entity requested.
        ident = mem.store.get_identity(args.layer, args.key)
        if not ident:
            print(f"No identity found for layer={args.layer!r} key={args.key!r}", file=sys.stderr)
            sys.exit(1)
        targets.append((args.layer, args.key, ident.content))
    elif args.layer:
        for ident in mem.store.get_identity_by_layer(args.layer):
            targets.append((args.layer, ident.key, ident.content))
    else:
        # Default: all personas and journeys.
        for ident in mem.store.get_identity_by_layer("persona"):
            targets.append(("persona", ident.key, ident.content))
        for ident in mem.store.get_identity_by_layer("journey"):
            targets.append(("journey", ident.key, ident.content))

    if not targets:
        print("No entities found to describe.")
        return

    generated = 0
    for layer, key, content in targets:
        print(f"  generating {layer}/{key}...", end=" ", flush=True)
        descriptor = generate_descriptor(content, layer=layer, key=key)
        if descriptor:
            mem.store.upsert_descriptor(layer, key, descriptor)
            print(f"done — {descriptor[:80]}{'...' if len(descriptor) > 80 else ''}")
            generated += 1
        else:
            print("skipped (empty response)")

    print(f"\n{generated}/{len(targets)} descriptors generated.")


def _cmd_list(args: argparse.Namespace) -> None:
    mem = MemoryClient(db_path=db_path_from_mirror_home(args.mirror_home))

    if args.layer:
        rows = [
            (args.layer, key, desc)
            for key, desc in mem.store.get_descriptors_by_layer(args.layer).items()
        ]
    else:
        # All layers.
        rows = []
        for ident in mem.store.get_all_identity():
            d = mem.store.get_descriptor(ident.layer, ident.key)
            if d:
                rows.append((d.layer, d.key, d.descriptor))

    if not rows:
        print("No descriptors stored.")
        return

    for layer, key, descriptor in rows:
        print(f"[{layer}/{key}]")
        print(f"  {descriptor}")
        print()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Manage routing descriptors")
    parser.add_argument("--mirror-home", default=None)
    sub = parser.add_subparsers(dest="subcommand")

    gen = sub.add_parser("generate", help="Generate descriptors via LLM")
    gen.add_argument("--layer", default=None, help="Identity layer (e.g. persona, journey)")
    gen.add_argument("--key", default=None, help="Identity key (e.g. engineer, mirror)")

    lst = sub.add_parser("list", help="List stored descriptors")
    lst.add_argument("--layer", default=None, help="Filter by layer")

    args = parser.parse_args(argv)

    if args.subcommand == "generate":
        _cmd_generate(args)
    elif args.subcommand == "list":
        _cmd_list(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
