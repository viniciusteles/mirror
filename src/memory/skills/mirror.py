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
from memory.config import LOG_LLM_CALLS, RECEPTION_ENABLED
from memory.hooks.mirror_state import write_state
from memory.intelligence.llm_router import LLMResponse

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
) -> tuple[str | None, str | None, list | None, bool]:
    """Resolve routing defaults. Returns (persona, journey, detected, touches_identity).

    Priority order (highest to lowest):
      1. Explicit args passed directly to load()
      2. Reception classifier (when MEMORY_RECEPTION=1) — can override sticky
      3. Session/global sticky defaults — fallback when reception is off or empty
      4. Keyword/embedding detection — final fallback

    touches_identity defaults True (full context) when reception is disabled.
    """
    # Phase 1 — explicit args (never overridden).
    resolved_persona = persona
    resolved_journey = journey
    detected: list | None = None
    touches_identity: bool = True  # full context when reception is off

    # Phase 2 — load sticky into holding vars; do NOT apply yet.
    # Reception gets to run before sticky is applied so it can override it.
    runtime_session = mem.store.get_runtime_session(session_id) if session_id else None
    session_persona: str | None = runtime_session.persona if runtime_session else None
    session_journey: str | None = runtime_session.journey if runtime_session else None

    if session_persona is None or session_journey is None:
        global_persona, global_journey = mem.store.get_latest_runtime_defaults(
            exclude_session_id=session_id
        )
        session_persona = session_persona or global_persona
        session_journey = session_journey or global_journey

    # Phase 3 — reception (when enabled, runs before sticky is applied).
    if RECEPTION_ENABLED and query:
        import json

        from memory.intelligence.reception import reception

        raw_personas = mem.store.get_identity_by_layer("persona")
        persona_descriptors = mem.store.get_descriptors_by_layer("persona")
        personas_meta = []
        for ident in raw_personas:
            try:
                meta = json.loads(ident.metadata) if ident.metadata else {}
            except (json.JSONDecodeError, TypeError):
                meta = {}
            description = persona_descriptors.get(ident.key) or (ident.content or "")[:200]
            personas_meta.append(
                {
                    "slug": ident.key,
                    "description": description,
                    "routing_keywords": meta.get("routing_keywords") or [],
                }
            )

        raw_journeys = mem.store.get_identity_by_layer("journey")
        journey_descriptors = mem.store.get_descriptors_by_layer("journey")
        journeys_meta = [
            {
                "slug": j.key,
                "description": journey_descriptors.get(j.key) or (j.content or "")[:200],
            }
            for j in raw_journeys
        ]

        llm_logger = None
        if LOG_LLM_CALLS:

            def llm_logger(response: LLMResponse) -> None:
                mem.store.log_llm_call(
                    role="reception",
                    model=response.model,
                    prompt=response.prompt or "",
                    response_text=response.content,
                    prompt_tokens=response.prompt_tokens,
                    completion_tokens=response.completion_tokens,
                    latency_ms=response.latency_ms,
                )

        result = reception(query, personas_meta, journeys_meta, on_llm_call=llm_logger)

        if result.personas and resolved_persona is None:
            resolved_persona = result.personas[0]
        if result.journey and resolved_journey is None:
            resolved_journey = result.journey
        touches_identity = result.touches_identity
        # touches_shadow available for E4.S4 shadow layer gating.

    # Phase 4 — apply sticky as fallback (reception was empty or disabled).
    if resolved_persona is None:
        resolved_persona = session_persona
    if resolved_journey is None:
        resolved_journey = session_journey

    # Phase 5 — keyword/embedding detection as final fallback.
    if resolved_persona is None and query:
        detected_personas = mem.detect_persona(query)
        if detected_personas:
            resolved_persona = detected_personas[0][0]

    if resolved_journey is None and query:
        detected = mem.detect_journey(query)
        if detected:
            resolved_journey = detected[0][0]

    return resolved_persona, resolved_journey, detected, touches_identity


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

    resolved_persona, resolved_journey, detected, touches_identity = _resolve_defaults(
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
        touches_identity=touches_identity,
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
