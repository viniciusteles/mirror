"""ConversationService read/query behavior."""

from memory.models import Conversation, Message


def test_find_by_id_prefix_returns_latest_matching_conversation(store, conversation_service):
    older = store.create_conversation(
        Conversation(
            id="abc11111", interface="cli", title="Older", started_at="2026-01-01T00:00:00Z"
        )
    )
    newer = store.create_conversation(
        Conversation(
            id="abc22222", interface="cli", title="Newer", started_at="2026-01-02T00:00:00Z"
        )
    )

    result = conversation_service.find_by_id_prefix("abc")

    assert result is not None
    assert result.id == newer.id
    assert result.id != older.id


def test_find_by_id_prefix_returns_none_when_not_found(conversation_service):
    assert conversation_service.find_by_id_prefix("missing") is None


def test_list_recent_returns_newest_first_with_message_count(store, conversation_service):
    older = store.create_conversation(
        Conversation(id="older", interface="cli", title="Older", started_at="2026-01-01T00:00:00Z")
    )
    newer = store.create_conversation(
        Conversation(id="newer", interface="cli", title="Newer", started_at="2026-01-02T00:00:00Z")
    )
    store.add_message(Message(conversation_id=newer.id, role="user", content="hello"))
    store.add_message(Message(conversation_id=newer.id, role="assistant", content="hi"))

    result = conversation_service.list_recent(limit=10)

    assert [item.id for item in result] == [newer.id, older.id]
    assert result[0].message_count == 2
    assert result[1].message_count == 0


def test_list_recent_filters_by_journey(store, conversation_service):
    store.create_conversation(
        Conversation(
            id="mirror", interface="cli", journey="mirror", started_at="2026-01-02T00:00:00Z"
        )
    )
    store.create_conversation(
        Conversation(
            id="other", interface="cli", journey="other", started_at="2026-01-01T00:00:00Z"
        )
    )

    result = conversation_service.list_recent(limit=10, journey="mirror")

    assert [item.id for item in result] == ["mirror"]


def test_list_recent_filters_by_persona(store, conversation_service):
    store.create_conversation(
        Conversation(
            id="engineer", interface="cli", persona="engineer", started_at="2026-01-02T00:00:00Z"
        )
    )
    store.create_conversation(
        Conversation(
            id="writer", interface="cli", persona="writer", started_at="2026-01-01T00:00:00Z"
        )
    )

    result = conversation_service.list_recent(limit=10, persona="engineer")

    assert [item.id for item in result] == ["engineer"]
