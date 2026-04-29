"""Tests for CV7.E4.S4 — shadow as structural cultivation.

Covers:
- get_shadow_candidate_memories(): query correctness
- Shadow composition in load_mirror_context(): gating logic
- propose_shadow_observations(): output parsing (mocked LLM)
- mm-shadow apply: identity update + readiness_state transition + provenance
- mm-shadow reject: status update, identity unchanged
- mm-shadow show: identity layer output
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from memory.models import Consolidation, Identity, Memory

# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def mem_client(tmp_path):
    from memory import MemoryClient

    client = MemoryClient(env="test", db_path=tmp_path / "test.db")
    yield client
    client.close()


def _make_memory(
    memory_type: str = "tension",
    layer: str = "shadow",
    readiness_state: str = "observed",
    title: str = "Test tension",
    content: str = "There is a recurring avoidance here.",
) -> Memory:
    return Memory(
        memory_type=memory_type,
        layer=layer,
        title=title,
        content=content,
        created_at="2026-01-01T00:00:00Z",
        readiness_state=readiness_state,
    )


# ---------------------------------------------------------------------------
# get_shadow_candidate_memories
# ---------------------------------------------------------------------------


class TestGetShadowCandidateMemories:
    def test_returns_shadow_layer_memories(self, mem_client):
        m = _make_memory(layer="shadow", readiness_state="observed")
        mem_client.store.create_memory(m)
        result = mem_client.store.get_shadow_candidate_memories()
        assert any(r.id == m.id for r in result)

    def test_returns_tension_type_from_any_layer(self, mem_client):
        m = _make_memory(memory_type="tension", layer="ego", readiness_state="observed")
        mem_client.store.create_memory(m)
        result = mem_client.store.get_shadow_candidate_memories()
        assert any(r.id == m.id for r in result)

    def test_returns_pattern_type(self, mem_client):
        m = _make_memory(memory_type="pattern", layer="ego", readiness_state="observed")
        mem_client.store.create_memory(m)
        result = mem_client.store.get_shadow_candidate_memories()
        assert any(r.id == m.id for r in result)

    def test_excludes_integrated_memories(self, mem_client):
        m = _make_memory(layer="shadow", readiness_state="integrated")
        mem_client.store.create_memory(m)
        result = mem_client.store.get_shadow_candidate_memories()
        assert not any(r.id == m.id for r in result)

    def test_includes_candidate_state(self, mem_client):
        m = _make_memory(layer="shadow", readiness_state="candidate")
        mem_client.store.create_memory(m)
        result = mem_client.store.get_shadow_candidate_memories()
        assert any(r.id == m.id for r in result)

    def test_excludes_non_shadow_non_tension_insight(self, mem_client):
        m = _make_memory(memory_type="insight", layer="ego", readiness_state="observed")
        mem_client.store.create_memory(m)
        result = mem_client.store.get_shadow_candidate_memories()
        assert not any(r.id == m.id for r in result)

    def test_respects_limit(self, mem_client):
        for i in range(5):
            mem_client.store.create_memory(_make_memory(title=f"T{i}"))
        result = mem_client.store.get_shadow_candidate_memories(limit=3)
        assert len(result) <= 3


# ---------------------------------------------------------------------------
# Shadow composition in load_mirror_context
# ---------------------------------------------------------------------------


class TestShadowComposition:
    def test_shadow_not_included_when_touches_shadow_false(self, mem_client):
        mem_client.store.upsert_identity(
            Identity(layer="shadow", key="profile", content="Shadow pattern content.")
        )
        ctx = mem_client.load_mirror_context(touches_shadow=False)
        assert "Shadow pattern content." not in ctx

    def test_shadow_not_included_when_no_shadow_content(self, mem_client):
        # No shadow identity entries — should not appear even if touches_shadow=True
        ctx = mem_client.load_mirror_context(touches_shadow=True)
        assert "shadow/profile" not in ctx

    def test_shadow_included_when_touches_shadow_and_has_content(self, mem_client):
        mem_client.store.upsert_identity(
            Identity(layer="shadow", key="profile", content="Recurring avoidance of conflict.")
        )
        ctx = mem_client.load_mirror_context(touches_shadow=True)
        assert "Recurring avoidance of conflict." in ctx

    def test_shadow_section_includes_provenance_framing(self, mem_client):
        mem_client.store.upsert_identity(
            Identity(layer="shadow", key="profile", content="Test pattern.")
        )
        ctx = mem_client.load_mirror_context(touches_shadow=True)
        assert "Confirmed shadow patterns" in ctx

    def test_shadow_includes_all_entries(self, mem_client):
        mem_client.store.upsert_identity(
            Identity(layer="shadow", key="profile", content="Pattern A.")
        )
        mem_client.store.upsert_identity(
            Identity(layer="shadow", key="blind-spots", content="Pattern B.")
        )
        ctx = mem_client.load_mirror_context(touches_shadow=True)
        assert "Pattern A." in ctx
        assert "Pattern B." in ctx

    def test_touches_identity_unaffected_by_touches_shadow(self, mem_client):
        # touches_shadow=True should not change behaviour of touches_identity
        mem_client.store.upsert_identity(
            Identity(layer="self", key="soul", content="Deep soul content.")
        )
        ctx_no_identity = mem_client.load_mirror_context(
            touches_identity=False, touches_shadow=False
        )
        ctx_with_identity = mem_client.load_mirror_context(
            touches_identity=True, touches_shadow=False
        )
        assert "Deep soul content." not in ctx_no_identity
        assert "Deep soul content." in ctx_with_identity


# ---------------------------------------------------------------------------
# propose_shadow_observations (mocked LLM)
# ---------------------------------------------------------------------------


class TestProposeShadowObservations:
    def test_empty_memories_returns_empty(self):
        from memory.intelligence.shadow import propose_shadow_observations

        result = propose_shadow_observations([], [], "Vinícius")
        assert result == []

    def test_parses_valid_llm_response(self):
        from memory.intelligence.shadow import propose_shadow_observations

        fake_response = MagicMock()
        fake_response.content = json.dumps(
            [
                {
                    "title": "Conflict avoidance",
                    "observation": "This has appeared in 3 contexts: avoidance of direct conflict.",
                    "memory_ids": ["abc123", "def456"],
                    "evidence_note": "appeared in 3 conversations over 4 weeks",
                }
            ]
        )

        mem = _make_memory()
        with patch("memory.intelligence.shadow.send_to_model", return_value=fake_response):
            results = propose_shadow_observations([mem], [], "Vinícius")

        assert len(results) == 1
        assert results[0].action == "shadow_observation"
        assert results[0].status == "pending"
        assert results[0].target_layer == "shadow"
        assert results[0].target_key == "profile"
        assert "Conflict avoidance" in results[0].proposal
        assert "abc123" in json.loads(results[0].source_memory_ids)

    def test_returns_empty_on_llm_failure(self):
        from memory.intelligence.shadow import propose_shadow_observations

        mem = _make_memory()
        with patch("memory.intelligence.shadow.send_to_model", side_effect=Exception("API error")):
            results = propose_shadow_observations([mem], [], "Vinícius")

        assert results == []

    def test_returns_empty_on_empty_llm_array(self):
        from memory.intelligence.shadow import propose_shadow_observations

        fake_response = MagicMock()
        fake_response.content = "[]"
        mem = _make_memory()
        with patch("memory.intelligence.shadow.send_to_model", return_value=fake_response):
            results = propose_shadow_observations([mem], [], "Vinícius")

        assert results == []

    def test_skips_items_without_observation(self):
        from memory.intelligence.shadow import propose_shadow_observations

        fake_response = MagicMock()
        fake_response.content = json.dumps(
            [{"title": "Missing obs", "observation": "", "memory_ids": []}]
        )
        mem = _make_memory()
        with patch("memory.intelligence.shadow.send_to_model", return_value=fake_response):
            results = propose_shadow_observations([mem], [], "Vinícius")

        assert results == []


# ---------------------------------------------------------------------------
# mm-shadow apply: write to shadow layer + advance readiness_state
# ---------------------------------------------------------------------------


class TestShadowApply:
    def test_apply_creates_shadow_identity_entry(self, mem_client, tmp_path):
        m = _make_memory()
        mem_client.store.create_memory(m)

        c = Consolidation(
            action="shadow_observation",
            proposal="**Conflict avoidance**\n\nRepeated pattern across 3 conversations.",
            source_memory_ids=json.dumps([m.id]),
            target_layer="shadow",
            target_key="profile",
            rationale="Conflict avoidance",
        )
        mem_client.store.create_consolidation(c)

        # Simulate apply
        result_content = c.proposal
        existing = mem_client.store.get_identity("shadow", "profile")
        if existing:
            updated = existing.content.rstrip() + "\n\n---\n\n" + result_content
        else:
            updated = result_content
        mem_client.store.upsert_identity(Identity(layer="shadow", key="profile", content=updated))
        mem_client.store.update_memory_readiness_state(m.id, "acknowledged")
        mem_client.store.update_consolidation_status(c.id, status="accepted", result=result_content)

        # Verify
        shadow = mem_client.store.get_identity("shadow", "profile")
        assert shadow is not None
        assert "Conflict avoidance" in shadow.content

        updated_mem = mem_client.store.get_memory(m.id)
        assert updated_mem.readiness_state == "acknowledged"

        updated_c = mem_client.store.get_consolidation(c.id)
        assert updated_c.status == "accepted"
        assert updated_c.result is not None

    def test_apply_appends_to_existing_shadow_layer(self, mem_client):
        mem_client.store.upsert_identity(
            Identity(layer="shadow", key="profile", content="First pattern.")
        )
        m = _make_memory()
        mem_client.store.create_memory(m)

        c = Consolidation(
            action="shadow_observation",
            proposal="Second pattern.",
            source_memory_ids=json.dumps([m.id]),
            target_layer="shadow",
            target_key="profile",
        )
        mem_client.store.create_consolidation(c)

        existing = mem_client.store.get_identity("shadow", "profile")
        updated = existing.content.rstrip() + "\n\n---\n\n" + "Second pattern."
        mem_client.store.upsert_identity(Identity(layer="shadow", key="profile", content=updated))

        result = mem_client.store.get_identity("shadow", "profile")
        assert "First pattern." in result.content
        assert "Second pattern." in result.content


# ---------------------------------------------------------------------------
# mm-shadow reject
# ---------------------------------------------------------------------------


class TestShadowReject:
    def test_reject_marks_consolidation_rejected(self, mem_client):
        c = Consolidation(
            action="shadow_observation",
            proposal="Rejected pattern.",
            source_memory_ids=json.dumps([]),
        )
        mem_client.store.create_consolidation(c)
        mem_client.store.update_consolidation_status(c.id, status="rejected")

        updated = mem_client.store.get_consolidation(c.id)
        assert updated.status == "rejected"

    def test_reject_does_not_change_shadow_identity(self, mem_client):
        mem_client.store.upsert_identity(
            Identity(layer="shadow", key="profile", content="Existing shadow.")
        )
        c = Consolidation(
            action="shadow_observation",
            proposal="New rejected pattern.",
            source_memory_ids=json.dumps([]),
        )
        mem_client.store.create_consolidation(c)
        mem_client.store.update_consolidation_status(c.id, status="rejected")

        shadow = mem_client.store.get_identity("shadow", "profile")
        assert shadow.content == "Existing shadow."


# ---------------------------------------------------------------------------
# shadow/profile identity layer — default absent
# ---------------------------------------------------------------------------


class TestShadowLayer:
    def test_shadow_layer_absent_by_default(self, mem_client):
        entries = mem_client.store.get_identity_by_layer("shadow")
        assert entries == []

    def test_shadow_layer_created_by_upsert(self, mem_client):
        mem_client.store.upsert_identity(
            Identity(layer="shadow", key="profile", content="First observation.")
        )
        entries = mem_client.store.get_identity_by_layer("shadow")
        assert len(entries) == 1
        assert entries[0].content == "First observation."

    def test_shadow_layer_multiple_keys(self, mem_client):
        mem_client.store.upsert_identity(Identity(layer="shadow", key="profile", content="A."))
        mem_client.store.upsert_identity(Identity(layer="shadow", key="blind-spots", content="B."))
        entries = mem_client.store.get_identity_by_layer("shadow")
        assert len(entries) == 2
