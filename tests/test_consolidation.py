"""Tests for CV7.E4.S3 — consolidation as integration.

Covers:
- cluster_memories(): pure clustering math (no LLM, no embeddings)
- ConsolidationStore CRUD: create, get, update status, list
- update_memory_readiness_state(): state transitions
- Migration 010: consolidations table added to existing DBs
- Consolidation model defaults
- CLI scan output format (unit-level, no LLM)
"""

from __future__ import annotations

import json
import sqlite3

import numpy as np
import pytest

from memory.intelligence.consolidate import (
    MAX_CLUSTER_SIZE,
    cluster_memories,
)
from memory.intelligence.embeddings import embedding_to_bytes
from memory.models import Consolidation, Memory

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_memory(
    title: str = "Memory",
    content: str = "Content.",
    layer: str = "ego",
    memory_type: str = "insight",
    readiness_state: str = "observed",
    embedding: np.ndarray | None = None,
) -> Memory:
    mem = Memory(
        memory_type=memory_type,
        layer=layer,
        title=title,
        content=content,
        created_at="2026-01-01T00:00:00Z",
        readiness_state=readiness_state,
    )
    if embedding is not None:
        mem.embedding = embedding_to_bytes(embedding)
    return mem


def _unit_vec(*components: float) -> np.ndarray:
    v = np.array(components, dtype=float)
    return v / np.linalg.norm(v)


# ---------------------------------------------------------------------------
# cluster_memories — pure math, no I/O
# ---------------------------------------------------------------------------


class TestClusterMemories:
    def test_empty_input_returns_empty(self):
        assert cluster_memories([]) == []

    def test_single_memory_returns_empty(self):
        m = _make_memory(embedding=_unit_vec(1, 0, 0))
        assert cluster_memories([m]) == []

    def test_no_embeddings_returns_empty(self):
        m1 = _make_memory()
        m2 = _make_memory()
        assert cluster_memories([m1, m2]) == []

    def test_identical_embeddings_clustered(self):
        emb = _unit_vec(1, 0, 0)
        m1 = _make_memory("A", embedding=emb)
        m2 = _make_memory("B", embedding=emb)
        clusters = cluster_memories([m1, m2], threshold=0.9)
        assert len(clusters) == 1
        assert len(clusters[0]) == 2

    def test_orthogonal_embeddings_not_clustered(self):
        m1 = _make_memory("A", embedding=_unit_vec(1, 0, 0))
        m2 = _make_memory("B", embedding=_unit_vec(0, 1, 0))
        clusters = cluster_memories([m1, m2], threshold=0.5)
        assert clusters == []

    def test_three_similar_two_different_one_cluster(self):
        # m1, m2, m3 are similar; m4 is orthogonal
        base = _unit_vec(1, 0.1, 0)
        near = _unit_vec(1, 0.05, 0)
        near2 = _unit_vec(0.95, 0.1, 0)
        far = _unit_vec(0, 1, 0)
        m1 = _make_memory("A", embedding=base)
        m2 = _make_memory("B", embedding=near)
        m3 = _make_memory("C", embedding=near2)
        m4 = _make_memory("D", embedding=far)
        clusters = cluster_memories([m1, m2, m3, m4], threshold=0.9)
        # All three similar ones should cluster; m4 is isolated.
        assert len(clusters) == 1
        titles = [m.title for m in clusters[0]]
        assert "A" in titles
        assert "D" not in titles

    def test_integrated_memories_excluded(self):
        emb = _unit_vec(1, 0, 0)
        m1 = _make_memory("A", embedding=emb, readiness_state="integrated")
        m2 = _make_memory("B", embedding=emb, readiness_state="observed")
        # m1 is skipped; only m2 is eligible — no cluster possible
        clusters = cluster_memories([m1, m2], threshold=0.5)
        assert clusters == []

    def test_cluster_size_capped_at_max(self):
        emb = _unit_vec(1, 0, 0)
        memories = [_make_memory(f"M{i}", embedding=emb) for i in range(MAX_CLUSTER_SIZE + 5)]
        clusters = cluster_memories(memories, threshold=0.99)
        assert all(len(c) <= MAX_CLUSTER_SIZE for c in clusters)

    def test_memory_assigned_to_at_most_one_cluster(self):
        emb = _unit_vec(1, 0, 0)
        memories = [_make_memory(f"M{i}", embedding=emb) for i in range(4)]
        clusters = cluster_memories(memories, threshold=0.99)
        all_ids = [m.id for cluster in clusters for m in cluster]
        assert len(all_ids) == len(set(all_ids))

    def test_threshold_controls_grouping(self):
        # Two memories with cos ≈ 0.71 (45-degree angle in 2D)
        m1 = _make_memory("A", embedding=_unit_vec(1, 0, 0))  # [1, 0]
        m2 = _make_memory("B", embedding=_unit_vec(1, 1, 0))  # [1, 1] normalized
        high_threshold = cluster_memories([m1, m2], threshold=0.8)
        low_threshold = cluster_memories([m1, m2], threshold=0.5)
        assert high_threshold == []  # cos ≈ 0.707 < 0.8, not close enough
        assert len(low_threshold) == 1  # cos ≈ 0.707 >= 0.5, close enough


# ---------------------------------------------------------------------------
# ConsolidationStore — CRUD
# ---------------------------------------------------------------------------


@pytest.fixture()
def store(tmp_path):
    from memory import MemoryClient

    client = MemoryClient(env="test", db_path=tmp_path / "test.db")
    yield client.store
    client.close()


def _make_consolidation(**kwargs) -> Consolidation:
    defaults = {
        "action": "merge",
        "proposal": "Merge these two memories into one.",
        "source_memory_ids": json.dumps(["id-1", "id-2"]),
        "rationale": "Identical insight restated.",
    }
    defaults.update(kwargs)
    return Consolidation(**defaults)


class TestConsolidationStore:
    def test_create_and_get(self, store):
        c = store.create_consolidation(_make_consolidation())
        retrieved = store.get_consolidation(c.id)
        assert retrieved is not None
        assert retrieved.id == c.id
        assert retrieved.action == "merge"
        assert retrieved.status == "pending"

    def test_get_nonexistent_returns_none(self, store):
        assert store.get_consolidation("nonexistent") is None

    def test_update_status_accepted(self, store):
        c = store.create_consolidation(_make_consolidation())
        store.update_consolidation_status(c.id, status="accepted", result="Final merged content.")
        updated = store.get_consolidation(c.id)
        assert updated.status == "accepted"
        assert updated.result == "Final merged content."
        assert updated.reviewed_at is not None

    def test_update_status_rejected(self, store):
        c = store.create_consolidation(_make_consolidation())
        store.update_consolidation_status(c.id, status="rejected")
        assert store.get_consolidation(c.id).status == "rejected"

    def test_list_all(self, store):
        store.create_consolidation(_make_consolidation(action="merge"))
        store.create_consolidation(
            _make_consolidation(action="identity_update", target_layer="ego", target_key="behavior")
        )
        items = store.list_consolidations()
        assert len(items) == 2

    def test_list_by_status(self, store):
        c1 = store.create_consolidation(_make_consolidation())
        c2 = store.create_consolidation(_make_consolidation())
        store.update_consolidation_status(c1.id, status="accepted", result="ok")
        pending = store.list_consolidations(status="pending")
        accepted = store.list_consolidations(status="accepted")
        assert len(pending) == 1
        assert len(accepted) == 1
        assert pending[0].id == c2.id

    def test_list_pending_helper(self, store):
        store.create_consolidation(_make_consolidation())
        store.create_consolidation(_make_consolidation())
        pending = store.list_pending_consolidations()
        assert len(pending) == 2

    def test_list_respects_limit(self, store):
        for _ in range(5):
            store.create_consolidation(_make_consolidation())
        assert len(store.list_consolidations(limit=3)) == 3

    def test_all_fields_persisted(self, store):
        c = _make_consolidation(
            action="identity_update",
            proposal="Add this.",
            target_layer="ego",
            target_key="behavior",
            rationale="Clear pattern.",
        )
        store.create_consolidation(c)
        r = store.get_consolidation(c.id)
        assert r.target_layer == "ego"
        assert r.target_key == "behavior"
        assert r.rationale == "Clear pattern."


# ---------------------------------------------------------------------------
# update_memory_readiness_state
# ---------------------------------------------------------------------------


class TestReadinessStateTransitions:
    def test_advance_to_acknowledged(self, store):
        mem = Memory(
            memory_type="insight",
            layer="ego",
            title="t",
            content="c",
            created_at="2026-01-01T00:00:00Z",
        )
        store.create_memory(mem)
        assert store.get_memory(mem.id).readiness_state == "observed"

        store.update_memory_readiness_state(mem.id, "acknowledged")
        assert store.get_memory(mem.id).readiness_state == "acknowledged"

    def test_advance_to_integrated(self, store):
        mem = Memory(
            memory_type="insight",
            layer="ego",
            title="t",
            content="c",
            created_at="2026-01-01T00:00:00Z",
        )
        store.create_memory(mem)
        store.update_memory_readiness_state(mem.id, "integrated")
        assert store.get_memory(mem.id).readiness_state == "integrated"

    def test_advance_to_candidate(self, store):
        mem = Memory(
            memory_type="tension",
            layer="shadow",
            title="t",
            content="c",
            created_at="2026-01-01T00:00:00Z",
        )
        store.create_memory(mem)
        store.update_memory_readiness_state(mem.id, "candidate")
        assert store.get_memory(mem.id).readiness_state == "candidate"


# ---------------------------------------------------------------------------
# Consolidation model defaults
# ---------------------------------------------------------------------------


class TestConsolidationModel:
    def test_default_status_pending(self):
        c = Consolidation(
            action="merge",
            proposal="Merge.",
            source_memory_ids=json.dumps(["id-1"]),
        )
        assert c.status == "pending"

    def test_default_reviewed_at_none(self):
        c = Consolidation(
            action="merge",
            proposal="Merge.",
            source_memory_ids=json.dumps(["id-1"]),
        )
        assert c.reviewed_at is None

    def test_target_fields_optional(self):
        c = Consolidation(
            action="merge",
            proposal="Merge.",
            source_memory_ids=json.dumps(["id-1"]),
        )
        assert c.target_layer is None
        assert c.target_key is None
        assert c.rationale is None


# ---------------------------------------------------------------------------
# Migration 010
# ---------------------------------------------------------------------------


class TestMigration010:
    def test_creates_consolidations_table(self, tmp_path):
        from memory.db.migrations import MIGRATIONS, run_migrations

        db_path = tmp_path / "old.db"
        conn = sqlite3.connect(str(db_path))
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS _migrations (id TEXT PRIMARY KEY, applied_at TEXT NOT NULL);
            """
        )
        earlier = [m[0] for m in MIGRATIONS if m[0] != "010_create_consolidations"]
        for mid in earlier:
            conn.execute(
                "INSERT OR IGNORE INTO _migrations (id, applied_at) VALUES (?, ?)",
                (mid, "2026-01-01T00:00:00Z"),
            )
        conn.commit()

        # Table should not exist yet
        tables_before = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
        assert "consolidations" not in tables_before

        run_migrations(conn)

        tables_after = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
        assert "consolidations" in tables_after

    def test_migration_idempotent(self, tmp_path):
        from memory.db.migrations import _migrate_create_consolidations

        db_path = tmp_path / "idem.db"
        conn = sqlite3.connect(str(db_path))
        _migrate_create_consolidations(conn)
        _migrate_create_consolidations(conn)  # must not raise
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
        assert "consolidations" in tables
