"""Focused tests for memory storage read models."""

from memory.models import Memory


def test_list_recent_memory_summaries_returns_newest_first(store):
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

    summaries = store.list_recent_memory_summaries(limit=10)

    assert [summary.id for summary in summaries] == [newer.id, older.id]
    assert summaries[0].title == "Newer"
    assert summaries[0].memory_type == "decision"


def test_list_recent_memory_summaries_filters_by_type_layer_and_journey(store):
    match = store.create_memory(
        Memory(
            id="match",
            title="Match",
            content="content",
            memory_type="insight",
            layer="self",
            journey="mirror",
            created_at="2026-01-03T00:00:00Z",
        )
    )
    store.create_memory(
        Memory(
            id="wrong-type",
            title="Wrong type",
            content="content",
            memory_type="decision",
            layer="self",
            journey="mirror",
            created_at="2026-01-02T00:00:00Z",
        )
    )
    store.create_memory(
        Memory(
            id="wrong-layer",
            title="Wrong layer",
            content="content",
            memory_type="insight",
            layer="ego",
            journey="mirror",
            created_at="2026-01-01T00:00:00Z",
        )
    )

    summaries = store.list_recent_memory_summaries(
        limit=10,
        memory_type="insight",
        layer="self",
        journey="mirror",
    )

    assert [summary.id for summary in summaries] == [match.id]


def test_count_memories_by_type_returns_grouped_counts(store):
    store.create_memory(Memory(title="One", content="content", memory_type="insight"))
    store.create_memory(Memory(title="Two", content="content", memory_type="insight"))
    store.create_memory(Memory(title="Three", content="content", memory_type="decision"))

    counts = dict(store.count_memories_by_type())

    assert counts == {"decision": 1, "insight": 2}
