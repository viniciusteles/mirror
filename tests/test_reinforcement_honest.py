"""Tests for CV7.E4.S2 — honest reinforcement scoring.

Covers:
- reinforcement_score() math: use vs retrieval, time decay
- hybrid_score() takes pre-computed reinforcement (not raw access_count)
- Memory model new fields (last_accessed_at, use_count, readiness_state)
- Storage: log_access updates last_accessed_at; log_use increments use_count
- Migration 009: adds columns to an existing database
"""

from __future__ import annotations

import math
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from memory.config import (
    REINFORCEMENT_DECAY_DAYS,
    REINFORCEMENT_RETRIEVAL_WEIGHT,
    REINFORCEMENT_USE_WEIGHT,
)
from memory.intelligence.search import hybrid_score, reinforcement_score
from memory.models import Memory

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _days_ago(days: float) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.isoformat().replace("+00:00", "Z")


# ---------------------------------------------------------------------------
# reinforcement_score — unit tests
# ---------------------------------------------------------------------------


class TestReinforcementScore:
    def test_zero_access_zero_use_returns_zero(self):
        assert reinforcement_score(0, 0, None) == 0.0

    def test_zero_access_with_last_accessed_still_zero(self):
        # access_count=0 → retrieval_raw=0 regardless of timestamp
        score = reinforcement_score(0, 0, _days_ago(1))
        assert score == 0.0

    def test_use_count_only_no_access(self):
        # use_signal = min(1, 1/5) = 0.2; retrieval=0
        score = reinforcement_score(0, 1, None)
        expected = REINFORCEMENT_USE_WEIGHT * 0.2
        assert abs(score - expected) < 1e-9

    def test_use_count_saturates_at_five(self):
        score_5 = reinforcement_score(0, 5, None)
        score_10 = reinforcement_score(0, 10, None)
        assert abs(score_5 - score_10) < 1e-9  # both saturate use_signal at 1.0

    def test_retrieval_only_today_no_decay(self):
        # access_count=3, use=0, last_accessed today
        score = reinforcement_score(3, 0, _days_ago(0))
        retrieval_raw = min(1.0, math.log1p(3) / 3.0)
        # decay ≈ 1.0 for 0 days
        expected = REINFORCEMENT_RETRIEVAL_WEIGHT * retrieval_raw
        assert abs(score - expected) < 0.01

    def test_decay_halves_at_half_life(self):
        fresh = reinforcement_score(5, 0, _days_ago(0))
        stale = reinforcement_score(5, 0, _days_ago(REINFORCEMENT_DECAY_DAYS))
        ratio = stale / fresh
        assert 0.45 <= ratio <= 0.55, f"Expected ratio ~0.5, got {ratio:.4f}"

    def test_recent_beats_stale_same_access_count(self):
        recent = reinforcement_score(3, 0, _days_ago(1))
        stale = reinforcement_score(3, 0, _days_ago(REINFORCEMENT_DECAY_DAYS * 5))
        assert recent > stale

    def test_use_beats_many_retrievals(self):
        last = _days_ago(10)
        high_use = reinforcement_score(1, 10, last)
        many_retrievals = reinforcement_score(50, 0, last)
        assert high_use > many_retrievals

    def test_use_weight_is_dominant_component(self):
        # Saturated use, no retrieval
        max_use = reinforcement_score(0, 100, None)
        expected = REINFORCEMENT_USE_WEIGHT * 1.0
        assert abs(max_use - expected) < 1e-9

    def test_retrieval_ceiling_equals_retrieval_weight(self):
        # Very high access count → retrieval_raw → 1.0; today → decay ≈ 1.0
        score = reinforcement_score(100_000, 0, _days_ago(0))
        assert abs(score - REINFORCEMENT_RETRIEVAL_WEIGHT) < 0.01

    def test_no_last_accessed_at_when_access_count_positive(self):
        # Edge case: access_count > 0 but no cached timestamp (pre-migration rows).
        # No decay is applied — retrieval_raw used as-is.
        score = reinforcement_score(3, 0, None)
        retrieval_raw = min(1.0, math.log1p(3) / 3.0)
        expected = REINFORCEMENT_RETRIEVAL_WEIGHT * retrieval_raw
        assert abs(score - expected) < 1e-9

    def test_combined_use_and_retrieval(self):
        score = reinforcement_score(5, 3, _days_ago(7))
        assert 0.0 < score <= 1.0  # composite, just check it's in range

    def test_offset_aware_last_accessed_at_is_supported(self):
        last = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        score = reinforcement_score(3, 0, last)
        assert score > 0.0

    def test_non_utc_offset_last_accessed_at_is_normalized(self):
        offset = timezone(timedelta(hours=-3))
        last = (datetime.now(timezone.utc) - timedelta(days=1)).astimezone(offset).isoformat()
        score = reinforcement_score(3, 0, last)
        assert score > 0.0


# ---------------------------------------------------------------------------
# hybrid_score — now takes pre-computed reinforcement
# ---------------------------------------------------------------------------


class TestHybridScore:
    def test_higher_reinforcement_raises_score(self):
        base = hybrid_score(semantic=0.5, recency=0.5, reinforcement=0.0, relevance=0.5)
        higher = hybrid_score(semantic=0.5, recency=0.5, reinforcement=0.5, relevance=0.5)
        assert higher > base

    def test_zero_all_signals_returns_zero(self):
        assert hybrid_score(0.0, 0.0, 0.0, 0.0) == 0.0

    def test_weights_sum_to_one_gives_max_one(self):
        # All signals at 1.0 → score == sum of weights (should be 1.0 if weights sum to 1)
        from memory.config import SEARCH_WEIGHTS

        score = hybrid_score(1.0, 1.0, 1.0, 1.0)
        expected = sum(
            SEARCH_WEIGHTS[k] for k in ("semantic", "recency", "reinforcement", "relevance")
        )
        assert abs(score - expected) < 1e-9


# ---------------------------------------------------------------------------
# Memory model — new fields
# ---------------------------------------------------------------------------


class TestMemoryNewFields:
    def test_default_readiness_state(self):
        mem = Memory(
            memory_type="insight",
            layer="ego",
            title="t",
            content="c",
            created_at="2026-01-01T00:00:00Z",
        )
        assert mem.readiness_state == "observed"

    def test_default_use_count(self):
        mem = Memory(
            memory_type="insight",
            layer="ego",
            title="t",
            content="c",
            created_at="2026-01-01T00:00:00Z",
        )
        assert mem.use_count == 0

    def test_default_last_accessed_at(self):
        mem = Memory(
            memory_type="insight",
            layer="ego",
            title="t",
            content="c",
            created_at="2026-01-01T00:00:00Z",
        )
        assert mem.last_accessed_at is None

    def test_custom_readiness_state(self):
        mem = Memory(
            memory_type="insight",
            layer="ego",
            title="t",
            content="c",
            created_at="2026-01-01T00:00:00Z",
            readiness_state="acknowledged",
        )
        assert mem.readiness_state == "acknowledged"


# ---------------------------------------------------------------------------
# Storage — log_access sets last_accessed_at; log_use increments use_count
# ---------------------------------------------------------------------------


@pytest.fixture()
def mem_store(tmp_path):
    """An isolated Store backed by a temp database (schema + migrations applied)."""
    from memory import MemoryClient

    # Keep client alive for the duration of the test so __del__ doesn't close the conn.
    client = MemoryClient(env="test", db_path=tmp_path / "test.db")
    yield client.store, client.store.conn
    client.close()


def _make_memory() -> Memory:
    return Memory(
        memory_type="insight",
        layer="ego",
        title="Test memory",
        content="Something important",
        created_at=_days_ago(10),
    )


class TestLogAccess:
    def test_log_access_sets_last_accessed_at(self, mem_store):
        store, _conn = mem_store
        mem = store.create_memory(_make_memory())
        assert store.get_memory(mem.id).last_accessed_at is None

        store.log_access(mem.id, context="test query")

        updated = store.get_memory(mem.id)
        assert updated.last_accessed_at is not None

    def test_log_access_updates_last_accessed_at_on_second_call(self, mem_store):
        import time

        store, _conn = mem_store
        mem = store.create_memory(_make_memory())

        store.log_access(mem.id, context="first")
        first_ts = store.get_memory(mem.id).last_accessed_at

        time.sleep(0.01)  # ensure clock advances

        store.log_access(mem.id, context="second")
        second_ts = store.get_memory(mem.id).last_accessed_at

        assert second_ts >= first_ts

    def test_log_access_does_not_change_use_count(self, mem_store):
        store, _conn = mem_store
        mem = store.create_memory(_make_memory())
        store.log_access(mem.id)
        assert store.get_memory(mem.id).use_count == 0


class TestLogUse:
    def test_log_use_increments_use_count(self, mem_store):
        store, _conn = mem_store
        mem = store.create_memory(_make_memory())
        assert store.get_memory(mem.id).use_count == 0

        store.log_use(mem.id)
        assert store.get_memory(mem.id).use_count == 1

        store.log_use(mem.id)
        assert store.get_memory(mem.id).use_count == 2

    def test_log_use_does_not_write_access_log(self, mem_store):
        store, _conn = mem_store
        mem = store.create_memory(_make_memory())
        store.log_use(mem.id)
        count = store.get_access_count(mem.id)
        assert count == 0  # log_use != log_access

    def test_log_use_does_not_set_last_accessed_at(self, mem_store):
        store, _conn = mem_store
        mem = store.create_memory(_make_memory())
        store.log_use(mem.id)
        assert store.get_memory(mem.id).last_accessed_at is None


# ---------------------------------------------------------------------------
# Migration 009 — adds columns to an existing database
# ---------------------------------------------------------------------------


class TestMigration009:
    def test_adds_columns_to_existing_db(self, tmp_path):
        """Simulate an old database (pre-009) and verify migration adds columns."""
        from memory.db.migrations import MIGRATIONS, run_migrations

        db_path = tmp_path / "old.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row

        # Bootstrap schema (includes the columns in SCHEMA already, so use a stripped version)
        # Build a memories table WITHOUT the new columns to simulate old state
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                conversation_id TEXT,
                memory_type TEXT NOT NULL,
                layer TEXT NOT NULL DEFAULT 'ego',
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                context TEXT,
                journey TEXT,
                persona TEXT,
                tags TEXT,
                created_at TEXT NOT NULL,
                relevance_score REAL DEFAULT 1.0,
                embedding BLOB,
                metadata TEXT
            );
            CREATE TABLE IF NOT EXISTS _migrations (id TEXT PRIMARY KEY, applied_at TEXT NOT NULL);
            """
        )
        # Mark all earlier migrations as done so only 009 runs
        earlier = [m[0] for m in MIGRATIONS if m[0] != "009_memories_reinforcement_columns"]
        for mid in earlier:
            conn.execute(
                "INSERT OR IGNORE INTO _migrations (id, applied_at) VALUES (?, ?)",
                (mid, "2026-01-01T00:00:00Z"),
            )
        conn.commit()

        # Verify columns are absent before migration
        cols_before = {row[1] for row in conn.execute("PRAGMA table_info(memories)").fetchall()}
        assert "last_accessed_at" not in cols_before
        assert "use_count" not in cols_before
        assert "readiness_state" not in cols_before

        run_migrations(conn)

        cols_after = {row[1] for row in conn.execute("PRAGMA table_info(memories)").fetchall()}
        assert "last_accessed_at" in cols_after
        assert "use_count" in cols_after
        assert "readiness_state" in cols_after

    def test_migration_is_idempotent(self, tmp_path):
        """Running migration 009 twice is a no-op (no error, no duplicate columns)."""
        from memory.db.migrations import _migrate_memories_reinforcement_columns

        db_path = tmp_path / "idem.db"
        conn = sqlite3.connect(str(db_path))
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                memory_type TEXT NOT NULL,
                layer TEXT NOT NULL DEFAULT 'ego',
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )

        _migrate_memories_reinforcement_columns(conn)
        _migrate_memories_reinforcement_columns(conn)  # must not raise

        cols = {row[1] for row in conn.execute("PRAGMA table_info(memories)").fetchall()}
        assert "last_accessed_at" in cols

    def test_existing_rows_get_default_values(self, tmp_path):
        """After migration, existing rows return default values for new columns."""
        from memory.db.migrations import _migrate_memories_reinforcement_columns

        db_path = tmp_path / "defaults.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                memory_type TEXT NOT NULL,
                layer TEXT NOT NULL DEFAULT 'ego',
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            INSERT INTO memories (id, memory_type, layer, title, content, created_at)
            VALUES ('m1', 'insight', 'ego', 'Old memory', 'content', '2024-01-01T00:00:00Z');
            """
        )

        _migrate_memories_reinforcement_columns(conn)

        row = conn.execute("SELECT * FROM memories WHERE id = 'm1'").fetchone()
        assert row["use_count"] == 0
        assert row["readiness_state"] == "observed"
        assert row["last_accessed_at"] is None
