"""Extraction eval: memory extraction quality on canned conversation transcripts.

Each probe calls extract_memories() against a fixed transcript and checks
whether the output satisfies an expected shape.

Run with:
    uv run python -m memory eval extraction

Requires OPENROUTER_API_KEY. Costs a few cents per run.
"""

from __future__ import annotations

from evals.types import EvalProbe
from memory.intelligence.extraction import extract_memories
from memory.models import ExtractedMemory, Message

THRESHOLD = 0.8


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _msgs(*pairs: tuple[str, str]) -> list[Message]:
    """Build a Message list from (role, content) pairs."""
    return [Message(conversation_id="eval", role=r, content=c) for r, c in pairs]


def _has_type(memories: list[ExtractedMemory], *types: str) -> bool:
    return any(m.memory_type in types for m in memories)


def _has_layer(memories: list[ExtractedMemory], *layers: str) -> bool:
    return any(m.layer in layers for m in memories)


def _summary(memories: list[ExtractedMemory]) -> str:
    if not memories:
        return "0 memories extracted"
    parts = [f"{m.memory_type}/{m.layer}" for m in memories]
    return f"{len(memories)} memories: {', '.join(parts)}"


# ---------------------------------------------------------------------------
# Probes
# ---------------------------------------------------------------------------


def _probe_engineering_decision() -> tuple[bool, str]:
    """Should extract a decision or learning memory in the ego layer."""
    messages = _msgs(
        (
            "user",
            "I've been thinking about the auth module. It's doing too much — "
            "validation, session management, and rate limiting all in one place.",
        ),
        ("assistant", "That's a classic single-responsibility violation. What's your plan?"),
        (
            "user",
            "I'm going to split it into three focused modules. It'll take a sprint "
            "but the coupling is already causing bugs. I've decided to do it now "
            "before we add OAuth.",
        ),
        (
            "assistant",
            "Good call. Doing it before OAuth saves you from untangling it later. "
            "The right time to refactor is before adding complexity, not after.",
        ),
        (
            "user",
            "Exactly. I've learned that deferring this kind of thing always costs more "
            "than it saves. We start Monday.",
        ),
    )
    memories = extract_memories(messages, journey="eval")
    notes = _summary(memories)
    passed = (
        len(memories) >= 1
        and _has_type(memories, "decision", "learning", "commitment")
        and _has_layer(memories, "ego")
    )
    return passed, notes


def _probe_existential_reflection() -> tuple[bool, str]:
    """Should extract an insight or reflection memory in the self or ego layer."""
    messages = _msgs(
        (
            "user",
            "I keep asking myself whether I'm building things that actually matter, "
            "or just keeping busy to avoid that question.",
        ),
        (
            "assistant",
            "That tension between motion and meaning — it's one of the most "
            "honest things you can notice about yourself.",
        ),
        (
            "user",
            "I think I've confused productivity with purpose for a long time. "
            "Getting things done felt like progress, but progress toward what?",
        ),
        ("assistant", "The question itself is the shift. Most people never ask it."),
        (
            "user",
            "I think what I actually want is to build things that change how people "
            "relate to their own freedom. Not just tools — something more like mirrors.",
        ),
    )
    memories = extract_memories(messages, journey="eval")
    notes = _summary(memories)
    passed = (
        len(memories) >= 1
        and _has_type(memories, "insight", "reflection", "tension")
        and _has_layer(memories, "self", "ego")
    )
    return passed, notes


def _probe_tension_shadow() -> tuple[bool, str]:
    """Should extract a tension memory, ideally in the shadow or ego layer."""
    messages = _msgs(
        (
            "user",
            "There's a conversation I need to have with my co-founder about equity "
            "and I keep finding reasons to postpone it.",
        ),
        ("assistant", "What do you think you're avoiding?"),
        (
            "user",
            "Conflict, probably. Or maybe the answer. If we have the conversation "
            "and it goes badly, that's a much harder problem than just not knowing.",
        ),
        (
            "assistant",
            "So the postponement is protecting something — the possibility that "
            "it could still be okay.",
        ),
        (
            "user",
            "Yeah. I've noticed I do this a lot. Avoiding the thing that would give "
            "me clarity because clarity might be uncomfortable.",
        ),
    )
    memories = extract_memories(messages, journey="eval")
    notes = _summary(memories)
    passed = (
        len(memories) >= 1
        and _has_type(memories, "tension", "pattern", "insight")
        and _has_layer(memories, "shadow", "ego")
    )
    return passed, notes


def _probe_trivial_no_memory() -> tuple[bool, str]:
    """Trivial exchange — should extract zero memories."""
    messages = _msgs(
        ("user", "Hey, what time is it?"),
        ("assistant", "I don't have access to real-time data, so I can't tell you the exact time."),
        ("user", "Oh right, never mind. Thanks."),
    )
    memories = extract_memories(messages, journey="eval")
    notes = _summary(memories)
    passed = len(memories) == 0
    return passed, notes


def _probe_commitment() -> tuple[bool, str]:
    """Should extract a commitment memory in the ego layer."""
    messages = _msgs(
        (
            "user",
            "I've been putting off writing the weekly update for my investors. "
            "I need to just do it.",
        ),
        ("assistant", "What's getting in the way?"),
        (
            "user",
            "Perfectionism, mostly. I want it to be good and that's making me not "
            "start at all. But they need visibility and I owe them that.",
        ),
        (
            "assistant",
            "Done is better than perfect here. A clear, honest update sent "
            "on time builds more trust than a polished one sent late.",
        ),
        ("user", "You're right. I'm committing to sending it by Friday, even if it's rough."),
    )
    memories = extract_memories(messages, journey="eval")
    notes = _summary(memories)
    passed = len(memories) >= 1 and _has_type(memories, "commitment", "decision")
    return passed, notes


# ---------------------------------------------------------------------------
# Probe registry
# ---------------------------------------------------------------------------

PROBES: list[EvalProbe] = [
    EvalProbe(
        id="engineering-decision",
        description="extracts decision/learning memory from a refactoring conversation",
        run=_probe_engineering_decision,
    ),
    EvalProbe(
        id="existential-reflection",
        description="extracts insight/reflection from a purpose conversation",
        run=_probe_existential_reflection,
    ),
    EvalProbe(
        id="tension-shadow",
        description="extracts tension/pattern from an avoidance conversation",
        run=_probe_tension_shadow,
    ),
    EvalProbe(
        id="trivial-no-memory",
        description="extracts zero memories from a trivial exchange",
        run=_probe_trivial_no_memory,
    ),
    EvalProbe(
        id="commitment",
        description="extracts commitment memory from an investor update conversation",
        run=_probe_commitment,
    ),
]
