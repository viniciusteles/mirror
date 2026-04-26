"""MemoryService read/query behavior."""

from memory.models import Memory


def test_list_recent_returns_newest_first(store, memory_service):
    older = store.create_memory(
        Memory(
            id="older",
            title="Older",
            content="older content",
            memory_type="insight",
            created_at="2026-01-01T00:00:00Z",
        )
    )
    newer = store.create_memory(
        Memory(
            id="newer",
            title="Newer",
            content="newer content",
            memory_type="decision",
            created_at="2026-01-02T00:00:00Z",
        )
    )

    result = memory_service.list_recent(limit=10)

    assert [item.id for item in result] == [newer.id, older.id]


def test_list_recent_filters_by_memory_type(store, memory_service):
    store.create_memory(Memory(title="Insight", content="content", memory_type="insight"))
    store.create_memory(Memory(title="Decision", content="content", memory_type="decision"))

    result = memory_service.list_recent(limit=10, memory_type="decision")

    assert [item.memory_type for item in result] == ["decision"]


def test_list_recent_filters_by_layer(store, memory_service):
    store.create_memory(Memory(title="Ego", content="content", memory_type="insight", layer="ego"))
    store.create_memory(
        Memory(title="Self", content="content", memory_type="insight", layer="self")
    )

    result = memory_service.list_recent(limit=10, layer="self")

    assert [item.layer for item in result] == ["self"]


def test_list_recent_filters_by_journey(store, memory_service):
    store.create_memory(
        Memory(title="Mirror", content="content", memory_type="insight", journey="mirror")
    )
    store.create_memory(
        Memory(title="Other", content="content", memory_type="insight", journey="other")
    )

    result = memory_service.list_recent(limit=10, journey="mirror")

    assert [item.journey for item in result] == ["mirror"]


def test_count_by_type_returns_grouped_counts(store, memory_service):
    store.create_memory(Memory(title="One", content="content", memory_type="insight"))
    store.create_memory(Memory(title="Two", content="content", memory_type="insight"))
    store.create_memory(Memory(title="Three", content="content", memory_type="decision"))

    result = dict(memory_service.count_by_type())

    assert result == {"decision": 1, "insight": 2}
