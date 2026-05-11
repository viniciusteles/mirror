"""Mirror Mode context dispatch for extensions.

Given the active persona / journey at a Mirror Mode turn, this module
finds every extension capability bound to that target, loads the
matching extensions, calls their providers, and returns the assembled
context sections.

Failures here never propagate. A provider that raises is logged and
skipped; a missing extension on disk is logged and skipped. The mirror
must always be able to answer, even if every extension is broken.
"""

from __future__ import annotations

import logging
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from memory.config import default_extensions_dir_for_home
from memory.extensions.api import ContextRequest
from memory.extensions.errors import ExtensionError
from memory.extensions.loader import load_extension

_logger = logging.getLogger("memory.extensions.context")


@dataclass(frozen=True)
class ContextSection:
    """One block of extension-provided text, ready for prompt injection."""

    extension_id: str
    capability_id: str
    binding_kind: str
    binding_target: str | None
    text: str

    @property
    def header(self) -> str:
        return f"=== extension/{self.extension_id}/{self.capability_id} ==="

    def rendered(self) -> str:
        return f"{self.header}\n{self.text}"


def _select_bindings(
    conn: sqlite3.Connection,
    *,
    persona_id: str | None,
    journey_id: str | None,
) -> list[sqlite3.Row]:
    """Return bindings that match the current persona/journey, in stable order.

    Stable order matters: providers must fire in a predictable sequence
    so prompt assembly is deterministic across reruns.
    """
    clauses: list[str] = []
    params: list[object] = []
    if persona_id:
        clauses.append("(target_kind = 'persona' AND target_id = ?)")
        params.append(persona_id)
    if journey_id:
        clauses.append("(target_kind = 'journey' AND target_id = ?)")
        params.append(journey_id)
    if not clauses:
        return []
    where = " OR ".join(clauses)
    return conn.execute(
        f"SELECT extension_id, capability_id, target_kind, target_id "
        f"FROM _ext_bindings WHERE {where} "
        f"ORDER BY extension_id, capability_id, target_kind, target_id",
        params,
    ).fetchall()


def collect_extension_context(
    conn: sqlite3.Connection,
    *,
    mirror_home: Path,
    persona_id: str | None,
    journey_id: str | None = None,
    user: str = "",
    query: str | None = None,
) -> list[ContextSection]:
    """Resolve bindings -> load extensions -> call providers -> collect text.

    Returns a list of :class:`ContextSection` (zero or more). Empty when
    no bindings match, all providers returned None, or every load failed.
    """
    bindings = _select_bindings(
        conn, persona_id=persona_id, journey_id=journey_id
    )
    if not bindings:
        return []

    sections: list[ContextSection] = []
    extensions_root = default_extensions_dir_for_home(mirror_home)

    for binding in bindings:
        extension_id = binding["extension_id"]
        capability_id = binding["capability_id"]
        ext_dir = extensions_root / extension_id
        if not ext_dir.exists():
            _logger.warning(
                "binding points to uninstalled extension extension_id=%s",
                extension_id,
            )
            continue

        try:
            api = load_extension(ext_dir, connection=conn)
        except ExtensionError as exc:
            _logger.warning(
                "extension failed to load extension_id=%s error=%s",
                extension_id,
                exc,
            )
            continue

        provider = api.context_registry.get(capability_id)
        if provider is None:
            _logger.warning(
                "binding references unknown capability extension_id=%s capability=%s",
                extension_id,
                capability_id,
            )
            continue

        request = ContextRequest(
            persona_id=persona_id,
            journey_id=journey_id,
            user=user,
            query=query,
            binding_kind=binding["target_kind"],
            binding_target=binding["target_id"],
        )

        try:
            text = provider(api, request)
        except Exception as exc:  # noqa: BLE001 — extensions are user code
            _logger.warning(
                "context provider raised extension_id=%s capability=%s error=%s",
                extension_id,
                capability_id,
                exc,
            )
            continue

        if not text:
            continue

        sections.append(
            ContextSection(
                extension_id=extension_id,
                capability_id=capability_id,
                binding_kind=binding["target_kind"],
                binding_target=binding["target_id"],
                text=str(text),
            )
        )

    return sections


def render_sections(sections: Iterable[ContextSection]) -> str:
    """Join sections into a single text block ready for prompt injection."""
    return "\n\n".join(section.rendered() for section in sections)
