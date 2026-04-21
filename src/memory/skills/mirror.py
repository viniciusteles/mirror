"""Mirror skill: core logic shared between Claude Code and Pi interfaces."""

from __future__ import annotations

import re
import sys

from memory.cli.conversation_logger import (
    is_muted,
    log_assistant_to_current,
    switch_conversation,
    update_current_conversation,
)
from memory.client import MemoryClient
from memory.hooks.mirror_state import write_state

_GLOBAL_STICKY_DEFAULTS_SESSION_ID = "__global_sticky_defaults__"


def _persist_global_sticky_defaults(
    mem: MemoryClient,
    *,
    persona: str | None,
    journey: str | None,
) -> None:
    """Persist cross-session sticky defaults even when no runtime session id exists."""
    if persona is None and journey is None:
        return
    mem.store.upsert_runtime_session(
        _GLOBAL_STICKY_DEFAULTS_SESSION_ID,
        interface="global_defaults",
        mirror_active=False,
        persona=persona,
        journey=journey,
        hook_injected=True,
        active=False,
    )


def _resolve_defaults(
    mem: MemoryClient,
    *,
    journey: str | None,
    persona: str | None,
    query: str | None,
    session_id: str | None,
) -> tuple[str | None, str | None, list | None]:
    """Resolve explicit + sticky + detected mirror defaults."""
    resolved_persona = persona
    resolved_journey = journey
    detected: list | None = None

    runtime_session = mem.store.get_runtime_session(session_id) if session_id else None

    if resolved_persona is None and runtime_session and runtime_session.persona:
        resolved_persona = runtime_session.persona
    if resolved_journey is None and runtime_session and runtime_session.journey:
        resolved_journey = runtime_session.journey

    if resolved_persona is None or resolved_journey is None:
        sticky_persona, sticky_journey = mem.store.get_latest_runtime_defaults(
            exclude_session_id=session_id
        )
        if resolved_persona is None:
            resolved_persona = sticky_persona
        if resolved_journey is None:
            resolved_journey = sticky_journey

    if resolved_persona is None and query:
        detected_personas = mem.detect_persona(query)
        if detected_personas:
            resolved_persona = detected_personas[0][0]

    if resolved_journey is None and query:
        detected = mem.detect_journey(query)
        if detected:
            resolved_journey = detected[0][0]

    return resolved_persona, resolved_journey, detected


def load(
    journey: str | None = None,
    persona: str | None = None,
    query: str | None = None,
    org: bool = False,
    context_only: bool = False,
    env: str | None = None,
    session_id: str | None = None,
) -> tuple[str, str | None, str | None, list | None]:
    """Activate Mirror Mode.

    Returns (context_str, resolved_persona, resolved_journey, detected_matches_or_None).
    Side effects: writes mirror state, switches conversation (unless context_only).
    """
    mem = MemoryClient(env=env)

    resolved_persona, resolved_journey, detected = _resolve_defaults(
        mem,
        journey=journey,
        persona=persona,
        query=query,
        session_id=session_id,
    )

    context = mem.load_mirror_context(
        persona=resolved_persona,
        journey=resolved_journey,
        org=org,
        query=query,
    )

    _persist_global_sticky_defaults(
        mem,
        persona=resolved_persona,
        journey=resolved_journey,
    )

    write_state(
        active=True,
        persona=resolved_persona,
        journey=resolved_journey,
        session_id=session_id,
    )

    if not context_only:
        switch_conversation(
            session_id=session_id,
            persona=resolved_persona,
            journey=resolved_journey,
        )

    return context, resolved_persona, resolved_journey, detected


def deactivate(session_id: str | None = None) -> None:
    """Clear mirror state for one session when a session id is available."""
    write_state(active=False, session_id=session_id)


def log(summary: str, session_id: str | None = None) -> None:
    """Record assistant response to a specific session. No-op if muted."""
    if is_muted():
        return
    log_assistant_to_current(summary, session_id=session_id)
    update_current_conversation(session_id=session_id, title=title_from_summary(summary))


def list_journeys(env: str | None = None) -> list[dict]:
    """Return active journeys as list of dicts."""
    mem = MemoryClient(env=env)
    return mem.list_active_journeys()


def title_from_summary(summary: str) -> str:
    """Extract a ≤60-char title from the first sentence of a summary."""
    first_sentence = re.split(r"[.!?]", summary, maxsplit=1)[0].strip()
    if len(first_sentence) > 60:
        first_sentence = first_sentence[:60].rsplit(" ", 1)[0] + "..."
    return first_sentence


PERSONA_ICONS: dict[str, str] = {
    "writer": "✒️",
    "therapist": "🪞",
    "doctor": "⚕️",
    "product-designer": "🎯",
    "engineer": "⚙️",
    "treasurer": "💰",
    "thinker": "💭",
    "scholar": "📖",
    "marketer": "📣",
    "teacher": "🎓",
    "mentor": "🧭",
    "researcher": "🔍",
    "traveler": "✈️",
}


def _print_mirror_banner(persona: str | None = None) -> None:
    print("\033[38;5;183m⏺ Mirror Mode active\033[0m", file=sys.stderr)
    if persona:
        icon = PERSONA_ICONS.get(persona, "◇")
        print(f"\033[38;5;183m  {icon} Persona: {persona}\033[0m", file=sys.stderr)
    else:
        print("\033[38;5;183m  Ego responding without persona\033[0m", file=sys.stderr)


def main(argv: list[str] | None = None) -> None:
    """CLI entry point for `python -m memory mirror ...`"""
    import argparse

    parser = argparse.ArgumentParser(description="Mirror skill")
    sub = parser.add_subparsers(dest="command", required=True)

    p_load = sub.add_parser("load", help="Load identity context")
    p_load.add_argument("--persona", help="Persona ID to load")
    p_load.add_argument("--journey", help="Journey ID to load")
    p_load.add_argument("--query", help="Attachment search terms")
    p_load.add_argument("--org", action="store_true", help="Include organization identity")
    p_load.add_argument(
        "--context-only",
        action="store_true",
        help="Load context without managing the conversation session",
    )
    p_load.add_argument("--session-id", help="Runtime session id for session-scoped mirror state")

    p_deactivate = sub.add_parser("deactivate", help="Deactivate Mirror Mode")
    p_deactivate.add_argument(
        "--session-id", help="Runtime session id for session-scoped mirror state"
    )

    p_log = sub.add_parser("log", help="Record a response summary")
    p_log.add_argument("summary", help="Concise response summary (2-3 sentences)")
    p_log.add_argument("--session-id", help="Runtime session id for session-scoped logging")

    sub.add_parser("journeys", help="List active journeys")

    args = parser.parse_args(argv)

    if args.command == "load":
        context, resolved_persona, _resolved_journey, detected = load(
            journey=args.journey,
            persona=args.persona,
            query=args.query,
            org=args.org,
            context_only=args.context_only,
            session_id=args.session_id,
        )
        if detected:
            j, score, match_type = detected[0]
            print(
                f"\033[38;5;183m  🧭 Journey detected: {j} ({match_type}, score: {score:.2f})\033[0m",
                file=sys.stderr,
            )
        _print_mirror_banner(resolved_persona)
        print(context)

    elif args.command == "deactivate":
        if not args.session_id:
            print(
                "warning: mirror deactivate invoked without --session-id; no state change.",
                file=sys.stderr,
            )
        else:
            deactivate(session_id=args.session_id)
            print("Mirror Mode deactivated.", file=sys.stderr)

    elif args.command == "log":
        log(args.summary, session_id=args.session_id)
        print("Response recorded.", file=sys.stderr)

    elif args.command == "journeys":
        for j in list_journeys():
            print(f"- **{j['id']}** — {j['name']}: {j['description']}")
