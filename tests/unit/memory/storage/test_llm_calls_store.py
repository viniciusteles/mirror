"""Unit tests for LLMCallStore storage component."""

import sqlite3

import pytest

from memory.db.schema import SCHEMA
from memory.storage.llm_calls import LLMCallStore

pytestmark = pytest.mark.unit


@pytest.fixture
def store():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    s = LLMCallStore()
    s.conn = conn
    return s


class TestLogLlmCall:
    def test_returns_string_id(self, store):
        row_id = store.log_llm_call(
            role="extraction",
            model="google/gemini-2.5-flash-lite",
            prompt="the prompt",
            response_text="the response",
        )
        assert isinstance(row_id, str)
        assert len(row_id) > 0

    def test_row_retrievable_by_role(self, store):
        store.log_llm_call(
            role="extraction",
            model="google/gemini-2.5-flash-lite",
            prompt="p",
            response_text="r",
        )
        rows = store.get_llm_calls(role="extraction")
        assert len(rows) == 1
        assert rows[0]["role"] == "extraction"

    def test_row_retrievable_by_conversation_id(self, store):
        # Insert a conversation so the FK is valid.
        store.conn.execute(
            "INSERT INTO conversations (id, started_at, interface) VALUES (?, ?, ?)",
            ("conv-1", "2026-01-01T00:00:00Z", "pi"),
        )
        store.log_llm_call(
            role="task_extraction",
            model="google/gemini-2.5-flash-lite",
            prompt="p",
            response_text="r",
            conversation_id="conv-1",
        )
        rows = store.get_llm_calls(conversation_id="conv-1")
        assert len(rows) == 1
        assert rows[0]["conversation_id"] == "conv-1"

    def test_all_fields_persisted(self, store):
        store.log_llm_call(
            role="journal_classification",
            model="some/model",
            prompt="my prompt",
            response_text="my response",
            prompt_tokens=10,
            completion_tokens=5,
            latency_ms=120,
            cost_usd=0.001,
            session_id="sess-abc",
        )
        rows = store.get_llm_calls(role="journal_classification")
        row = rows[0]
        assert row["model"] == "some/model"
        assert row["prompt"] == "my prompt"
        assert row["response"] == "my response"
        assert row["prompt_tokens"] == 10
        assert row["completion_tokens"] == 5
        assert row["latency_ms"] == 120
        assert row["cost_usd"] == pytest.approx(0.001)
        assert row["session_id"] == "sess-abc"

    def test_nullable_fields_default_to_none(self, store):
        store.log_llm_call(
            role="extraction",
            model="m",
            prompt="p",
            response_text="r",
        )
        rows = store.get_llm_calls(role="extraction")
        row = rows[0]
        assert row["prompt_tokens"] is None
        assert row["completion_tokens"] is None
        assert row["latency_ms"] is None
        assert row["cost_usd"] is None
        assert row["conversation_id"] is None
        assert row["session_id"] is None

    def test_called_at_is_iso_timestamp(self, store):
        store.log_llm_call(role="extraction", model="m", prompt="p", response_text="r")
        rows = store.get_llm_calls(role="extraction")
        called_at = rows[0]["called_at"]
        assert "T" in called_at  # ISO format contains T separator

    def test_results_ordered_newest_first(self, store):
        store.log_llm_call(role="extraction", model="m", prompt="first", response_text="r")
        store.log_llm_call(role="extraction", model="m", prompt="second", response_text="r")
        rows = store.get_llm_calls(role="extraction")
        assert rows[0]["prompt"] == "second"
        assert rows[1]["prompt"] == "first"

    def test_no_rows_without_matching_role(self, store):
        store.log_llm_call(role="extraction", model="m", prompt="p", response_text="r")
        rows = store.get_llm_calls(role="week_plan")
        assert rows == []

    def test_get_all_rows_without_filters(self, store):
        store.log_llm_call(role="extraction", model="m", prompt="p1", response_text="r")
        store.log_llm_call(role="week_plan", model="m", prompt="p2", response_text="r")
        rows = store.get_llm_calls()
        assert len(rows) == 2
