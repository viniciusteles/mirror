"""Fixture extension entrypoint.

Used by the extension-system test suite. Demonstrates the full
register(api) contract: declares CLI subcommands, registers a Mirror
Mode context provider, and writes to a single ext_hello_* table.
"""

from __future__ import annotations

from datetime import datetime, timezone

from memory.extensions.api import ContextRequest, ExtensionAPI


def register(api: ExtensionAPI) -> None:
    api.register_cli("ping", _cmd_ping, summary="Record a ping")
    api.register_cli("list", _cmd_list, summary="List recent pings")
    api.register_mirror_context("greeting", _provide_greeting)


def _cmd_ping(api: ExtensionAPI, args: list[str]) -> int:
    message = " ".join(args) or "hello"
    api.execute(
        "INSERT INTO ext_hello_pings (message, created_at) VALUES (?, ?)",
        (message, datetime.now(timezone.utc).isoformat()),
    )
    api.commit()
    print(f"ping: {message}")
    return 0


def _cmd_list(api: ExtensionAPI, args: list[str]) -> int:
    rows = api.read(
        "SELECT message, created_at FROM ext_hello_pings ORDER BY id DESC LIMIT 10"
    ).fetchall()
    if not rows:
        print("(no pings)")
        return 0
    for row in rows:
        print(f"{row['created_at']}  {row['message']}")
    return 0


def _provide_greeting(api: ExtensionAPI, ctx: ContextRequest) -> str | None:
    row = api.read("SELECT message FROM ext_hello_pings ORDER BY id DESC LIMIT 1").fetchone()
    if not row:
        return None
    return f"Latest ping: {row['message']}"
