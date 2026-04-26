"""Focused tests for conversation storage read models."""

from memory.models import Conversation, Message


def test_find_conversation_by_id_prefix_returns_latest_matching_conversation(store):
    older = store.create_conversation(
        Conversation(
            id="abc11111",
            interface="cli",
            title="Older",
            started_at="2026-01-01T00:00:00Z",
        )
    )
    newer = store.create_conversation(
        Conversation(
            id="abc22222",
            interface="cli",
            title="Newer",
            started_at="2026-01-02T00:00:00Z",
        )
    )

    result = store.find_conversation_by_id_prefix("abc")

    assert result is not None
    assert result.id == newer.id
    assert result.id != older.id


def test_find_conversation_by_id_prefix_returns_none_when_missing(store):
    assert store.find_conversation_by_id_prefix("missing") is None


def test_list_recent_conversation_summaries_includes_message_count(store):
    older = store.create_conversation(
        Conversation(id="older", interface="cli", title="Older", started_at="2026-01-01T00:00:00Z")
    )
    newer = store.create_conversation(
        Conversation(id="newer", interface="cli", title="Newer", started_at="2026-01-02T00:00:00Z")
    )
    store.add_message(Message(conversation_id=newer.id, role="user", content="hello"))
    store.add_message(Message(conversation_id=newer.id, role="assistant", content="hi"))

    summaries = store.list_recent_conversation_summaries(limit=10)

    assert [summary.id for summary in summaries] == [newer.id, older.id]
    assert summaries[0].message_count == 2
    assert summaries[1].message_count == 0


def test_list_recent_conversation_summaries_filters_by_journey_and_persona(store):
    match = store.create_conversation(
        Conversation(
            id="match",
            interface="cli",
            journey="mirror",
            persona="engineer",
            started_at="2026-01-03T00:00:00Z",
        )
    )
    store.create_conversation(
        Conversation(
            id="wrong-journey",
            interface="cli",
            journey="other",
            persona="engineer",
            started_at="2026-01-02T00:00:00Z",
        )
    )
    store.create_conversation(
        Conversation(
            id="wrong-persona",
            interface="cli",
            journey="mirror",
            persona="writer",
            started_at="2026-01-01T00:00:00Z",
        )
    )

    summaries = store.list_recent_conversation_summaries(
        limit=10,
        journey="mirror",
        persona="engineer",
    )

    assert [summary.id for summary in summaries] == [match.id]
