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


# ---------------------------------------------------------------------------
# fts_search
# ---------------------------------------------------------------------------


class TestFtsSearch:
    def test_returns_matching_memory_by_title_word(self, store):
        store.create_memory(
            Memory(
                title="Python refactoring decision",
                content="We split the module.",
                memory_type="decision",
            )
        )
        results = store.fts_search("Python")
        ids = [r[0] for r in results]
        assert any(ids), "Expected at least one FTS result"

    def test_returns_empty_for_no_match(self, store):
        store.create_memory(
            Memory(title="Irrelevant memory", content="Nothing here.", memory_type="insight")
        )
        results = store.fts_search("xyznonexistent")
        assert results == []

    def test_rank_scores_descend(self, store):
        store.create_memory(
            Memory(
                title="pricing pricing pricing", content="Lots of pricing.", memory_type="decision"
            )
        )
        store.create_memory(
            Memory(title="pricing once", content="Other content.", memory_type="decision")
        )
        results = store.fts_search("pricing")
        scores = [s for _, s in results]
        assert scores == sorted(scores, reverse=True)

    def test_respects_layer_filter(self, store):
        store.create_memory(
            Memory(
                title="auth refactor",
                content="Split auth module.",
                memory_type="decision",
                layer="ego",
            )
        )
        store.create_memory(
            Memory(
                title="auth insight", content="Auth is hard.", memory_type="insight", layer="self"
            )
        )
        results = store.fts_search("auth", layer="self")
        ids = [r[0] for r in results]
        assert len(ids) == 1

    def test_respects_journey_filter(self, store):
        store.create_memory(
            Memory(
                title="mirror build",
                content="Build step.",
                memory_type="decision",
                journey="mirror",
            )
        )
        store.create_memory(
            Memory(
                title="mirror plan", content="Plan step.", memory_type="decision", journey="other"
            )
        )
        results = store.fts_search("mirror", journey="mirror")
        assert len(results) == 1

    def test_new_memory_is_found_by_fts(self, store):
        store.create_memory(
            Memory(title="unique_term_xyz", content="Content.", memory_type="insight")
        )
        results = store.fts_search("unique_term_xyz")
        assert len(results) == 1

    def test_graceful_on_malformed_query(self, store):
        # FTS5 may raise OperationalError on syntax errors; should return []
        results = store.fts_search('AND OR NOT ""')
        assert isinstance(results, list)
