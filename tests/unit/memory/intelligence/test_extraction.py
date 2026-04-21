"""Unit tests for memory.intelligence.extraction."""

import json
from unittest.mock import MagicMock

import pytest

from memory.intelligence.extraction import (
    ExtractedTask,
    classify_journal_entry,
    extract_memories,
    extract_tasks,
    extract_week_plan,
    format_transcript,
)
from memory.models import ExtractedMemory, ExtractedWeekItem, Message

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_messages():
    return [
        Message(conversation_id="c1", role="user", content="Olá"),
        Message(conversation_id="c1", role="assistant", content="Oi"),
    ]


def _make_llm_mock(mocker, content: str) -> MagicMock:
    """Patch extraction.OpenAI to return `content` as the LLM response."""
    mock_choice = MagicMock()
    mock_choice.message.content = content

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_completion

    mocker.patch("memory.intelligence.extraction.OpenAI", return_value=mock_instance)
    mocker.patch("memory.intelligence.extraction.OPENROUTER_API_KEY", "test-key")
    return mock_instance


# ---------------------------------------------------------------------------
# format_transcript
# ---------------------------------------------------------------------------


class TestFormatTranscript:
    def test_user_label_defaults_to_user(self):
        msgs = [Message(conversation_id="c1", role="user", content="Question")]
        result = format_transcript(msgs)
        assert result == "**User:** Question"

    def test_user_label_uses_provided_name(self):
        msgs = [Message(conversation_id="c1", role="user", content="Question")]
        result = format_transcript(msgs, user_name="Vinicius")
        assert result == "**Vinicius:** Question"

    def test_assistant_becomes_mirror(self):
        msgs = [Message(conversation_id="c1", role="assistant", content="Answer")]
        result = format_transcript(msgs)
        assert result == "**Mirror:** Answer"

    def test_messages_joined_by_double_newline(self):
        msgs = [
            Message(conversation_id="c1", role="user", content="A"),
            Message(conversation_id="c1", role="assistant", content="B"),
        ]
        result = format_transcript(msgs)
        assert result == "**User:** A\n\n**Mirror:** B"

    def test_empty_list_returns_empty_string(self):
        assert format_transcript([]) == ""

    def test_system_role_becomes_mirror(self):
        msgs = [Message(conversation_id="c1", role="system", content="sys")]
        result = format_transcript(msgs)
        assert result == "**Mirror:** sys"


# ---------------------------------------------------------------------------
# extract_memories
# ---------------------------------------------------------------------------


class TestExtractMemories:
    def test_empty_messages_returns_empty_list(self):
        result = extract_memories([])
        assert result == []

    def test_returns_list_of_extracted_memory(self, mocker, sample_messages):
        payload = json.dumps(
            [{"title": "T", "content": "C", "memory_type": "insight", "layer": "ego", "tags": []}]
        )
        _make_llm_mock(mocker, payload)
        result = extract_memories(sample_messages)
        assert len(result) == 1
        assert isinstance(result[0], ExtractedMemory)

    def test_parsed_fields_match_llm_output(self, mocker, sample_messages):
        payload = json.dumps(
            [
                {
                    "title": "Tít",
                    "content": "Cont",
                    "memory_type": "decision",
                    "layer": "self",
                    "tags": ["a"],
                }
            ]
        )
        _make_llm_mock(mocker, payload)
        result = extract_memories(sample_messages)
        assert result[0].title == "Tít"
        assert result[0].content == "Cont"
        assert result[0].memory_type == "decision"
        assert result[0].layer == "self"
        assert result[0].tags == ["a"]

    def test_invalid_json_returns_empty_list(self, mocker, sample_messages):
        _make_llm_mock(mocker, "not valid json")
        result = extract_memories(sample_messages)
        assert result == []

    def test_non_list_json_returns_empty_list(self, mocker, sample_messages):
        _make_llm_mock(mocker, '{"key": "value"}')
        result = extract_memories(sample_messages)
        assert result == []

    def test_markdown_fenced_json_cleaned(self, mocker, sample_messages):
        payload = (
            "```json\n"
            + json.dumps(
                [
                    {
                        "title": "T",
                        "content": "C",
                        "memory_type": "insight",
                        "layer": "ego",
                        "tags": [],
                    }
                ]
            )
            + "\n```"
        )
        _make_llm_mock(mocker, payload)
        result = extract_memories(sample_messages)
        assert len(result) == 1

    def test_invalid_item_skipped(self, mocker, sample_messages):
        payload = json.dumps(
            [
                {
                    "title": "Valid",
                    "content": "C",
                    "memory_type": "insight",
                    "layer": "ego",
                    "tags": [],
                },
                {"title": "Missing type"},  # invalid
            ]
        )
        _make_llm_mock(mocker, payload)
        result = extract_memories(sample_messages)
        assert len(result) == 1
        assert result[0].title == "Valid"

    def test_persona_injected_when_llm_omits_it(self, mocker, sample_messages):
        payload = json.dumps(
            [{"title": "T", "content": "C", "memory_type": "insight", "layer": "ego", "tags": []}]
        )
        _make_llm_mock(mocker, payload)
        result = extract_memories(sample_messages, persona="mentor")
        assert result[0].persona == "mentor"

    def test_persona_not_overwritten_when_llm_provides_it(self, mocker, sample_messages):
        payload = json.dumps(
            [
                {
                    "title": "T",
                    "content": "C",
                    "memory_type": "insight",
                    "layer": "ego",
                    "tags": [],
                    "persona": "writer",
                }
            ]
        )
        _make_llm_mock(mocker, payload)
        result = extract_memories(sample_messages, persona="mentor")
        assert result[0].persona == "writer"

    def test_journey_injected_when_missing(self, mocker, sample_messages):
        payload = json.dumps(
            [{"title": "T", "content": "C", "memory_type": "insight", "layer": "ego", "tags": []}]
        )
        _make_llm_mock(mocker, payload)
        result = extract_memories(sample_messages, journey="reflexo")
        assert result[0].journey == "reflexo"

    def test_journey_not_overwritten(self, mocker, sample_messages):
        payload = json.dumps(
            [
                {
                    "title": "T",
                    "content": "C",
                    "memory_type": "insight",
                    "layer": "ego",
                    "tags": [],
                    "journey": "outro",
                }
            ]
        )
        _make_llm_mock(mocker, payload)
        result = extract_memories(sample_messages, journey="reflexo")
        assert result[0].journey == "outro"

    def test_stale_llm_journey_key_is_rejected(self, mocker, sample_messages):
        payload = json.dumps(
            [
                {
                    "title": "T",
                    "content": "C",
                    "memory_type": "insight",
                    "layer": "ego",
                    "tags": [],
                    "travessia": "legacy",
                }
            ]
        )
        _make_llm_mock(mocker, payload)
        result = extract_memories(sample_messages)
        assert result == []

    def test_prompt_requests_english_journey_key(self, mocker, sample_messages):
        mock_client = _make_llm_mock(mocker, "[]")
        extract_memories(sample_messages)
        prompt_content = mock_client.chat.completions.create.call_args[1]["messages"][0]["content"]
        assert '"journey": "..." or null' in prompt_content
        assert '"travessia"' not in prompt_content


# ---------------------------------------------------------------------------
# extract_tasks
# ---------------------------------------------------------------------------


class TestExtractTasks:
    def test_empty_messages_returns_empty_list(self):
        result = extract_tasks([])
        assert result == []

    def test_returns_extracted_task_objects(self, mocker, sample_messages):
        payload = json.dumps(
            [
                {
                    "title": "Fazer X",
                    "due_date": "2026-04-15",
                    "journey": None,
                    "stage": None,
                    "context": "ctx",
                }
            ]
        )
        _make_llm_mock(mocker, payload)
        result = extract_tasks(sample_messages)
        assert len(result) == 1
        assert isinstance(result[0], ExtractedTask)

    def test_title_field_mapped(self, mocker, sample_messages):
        payload = json.dumps(
            [
                {
                    "title": "Fazer X",
                    "due_date": None,
                    "journey": None,
                    "stage": None,
                    "context": None,
                }
            ]
        )
        _make_llm_mock(mocker, payload)
        result = extract_tasks(sample_messages)
        assert result[0].title == "Fazer X"

    def test_due_date_field_mapped(self, mocker, sample_messages):
        payload = json.dumps(
            [
                {
                    "title": "T",
                    "due_date": "2026-04-15",
                    "journey": None,
                    "stage": None,
                    "context": None,
                }
            ]
        )
        _make_llm_mock(mocker, payload)
        result = extract_tasks(sample_messages)
        assert result[0].due_date == "2026-04-15"

    def test_journey_fallback_from_argument(self, mocker, sample_messages):
        payload = json.dumps(
            [{"title": "T", "due_date": None, "journey": None, "stage": None, "context": None}]
        )
        _make_llm_mock(mocker, payload)
        result = extract_tasks(sample_messages, journey="reflexo")
        assert result[0].journey == "reflexo"

    def test_accepts_english_journey_from_llm(self, mocker, sample_messages):
        payload = json.dumps(
            [
                {
                    "title": "Do X",
                    "due_date": None,
                    "journey": "reflexo",
                    "stage": None,
                    "context": None,
                }
            ]
        )
        _make_llm_mock(mocker, payload)
        result = extract_tasks(sample_messages)
        assert result[0].journey == "reflexo"

    def test_stale_llm_journey_key_does_not_set_journey(self, mocker, sample_messages):
        payload = json.dumps(
            [
                {
                    "title": "Do X",
                    "due_date": None,
                    "travessia": "legacy",
                    "stage": None,
                    "context": None,
                }
            ]
        )
        _make_llm_mock(mocker, payload)
        result = extract_tasks(sample_messages)
        assert result[0].journey is None

    def test_prompt_requests_english_journey_key(self, mocker, sample_messages):
        mock_client = _make_llm_mock(mocker, "[]")
        extract_tasks(sample_messages)
        prompt_content = mock_client.chat.completions.create.call_args[1]["messages"][0]["content"]
        assert '"journey": "slug" or null' in prompt_content
        assert '"travessia"' not in prompt_content

    def test_invalid_json_returns_empty_list(self, mocker, sample_messages):
        _make_llm_mock(mocker, "garbage")
        result = extract_tasks(sample_messages)
        assert result == []

    def test_item_missing_title_skipped(self, mocker, sample_messages):
        payload = json.dumps([{"due_date": "2026-04-15"}])  # no title
        _make_llm_mock(mocker, payload)
        result = extract_tasks(sample_messages)
        assert result == []

    def test_markdown_fencing_cleaned(self, mocker, sample_messages):
        payload = (
            "```json\n"
            + json.dumps(
                [
                    {
                        "title": "T",
                        "due_date": None,
                        "journey": None,
                        "stage": None,
                        "context": None,
                    }
                ]
            )
            + "\n```"
        )
        _make_llm_mock(mocker, payload)
        result = extract_tasks(sample_messages)
        assert len(result) == 1


# ---------------------------------------------------------------------------
# extract_week_plan
# ---------------------------------------------------------------------------


class TestExtractWeekPlan:
    def test_returns_extracted_week_items(self, mocker):
        payload = json.dumps(
            [
                {
                    "title": "Reunião",
                    "due_date": "2026-04-14",
                    "scheduled_at": None,
                    "time_hint": None,
                    "journey": None,
                    "context": "",
                }
            ]
        )
        _make_llm_mock(mocker, payload)
        result = extract_week_plan("Tenho reunião amanhã", [])
        assert len(result) == 1
        assert isinstance(result[0], ExtractedWeekItem)

    def test_today_injected_into_prompt(self, mocker):
        import re

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="[]"))]
        )
        mocker.patch("memory.intelligence.extraction.OpenAI", return_value=mock_client)
        mocker.patch("memory.intelligence.extraction.OPENROUTER_API_KEY", "test-key")

        extract_week_plan("texto", [])
        call_args = mock_client.chat.completions.create.call_args
        prompt_content = call_args[1]["messages"][0]["content"]
        # Prompt deve conter uma data no formato YYYY-MM-DD
        assert re.search(r"\d{4}-\d{2}-\d{2}", prompt_content)

    def test_weekday_english_name_in_prompt(self, mocker):

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="[]"))]
        )
        mocker.patch("memory.intelligence.extraction.OpenAI", return_value=mock_client)
        mocker.patch("memory.intelligence.extraction.OPENROUTER_API_KEY", "test-key")

        extract_week_plan("texto", [])
        call_args = mock_client.chat.completions.create.call_args
        prompt_content = call_args[1]["messages"][0]["content"]
        weekdays = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        assert any(day in prompt_content for day in weekdays)

    def test_journey_context_formatted_in_prompt(self, mocker):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="[]"))]
        )
        mocker.patch("memory.intelligence.extraction.OpenAI", return_value=mock_client)
        mocker.patch("memory.intelligence.extraction.OPENROUTER_API_KEY", "test-key")

        extract_week_plan("texto", [{"slug": "reflexo", "description": "projeto de reflexão"}])
        call_args = mock_client.chat.completions.create.call_args
        prompt_content = call_args[1]["messages"][0]["content"]
        assert "reflexo" in prompt_content

    def test_empty_journey_context_shows_fallback(self, mocker):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="[]"))]
        )
        mocker.patch("memory.intelligence.extraction.OpenAI", return_value=mock_client)
        mocker.patch("memory.intelligence.extraction.OPENROUTER_API_KEY", "test-key")

        extract_week_plan("texto", [])
        call_args = mock_client.chat.completions.create.call_args
        prompt_content = call_args[1]["messages"][0]["content"]
        assert "no active journeys" in prompt_content

    def test_week_plan_prompt_requests_english_journey_key(self, mocker):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="[]"))]
        )
        mocker.patch("memory.intelligence.extraction.OpenAI", return_value=mock_client)
        mocker.patch("memory.intelligence.extraction.OPENROUTER_API_KEY", "test-key")

        extract_week_plan("text", [])
        call_args = mock_client.chat.completions.create.call_args
        prompt_content = call_args[1]["messages"][0]["content"]
        assert '"journey": "slug" or null' in prompt_content
        assert '"travessia"' not in prompt_content

    def test_stale_llm_journey_key_is_rejected(self, mocker):
        payload = json.dumps(
            [
                {
                    "title": "Reunião",
                    "due_date": "2026-04-14",
                    "scheduled_at": None,
                    "time_hint": None,
                    "travessia": "legacy",
                    "context": "",
                }
            ]
        )
        _make_llm_mock(mocker, payload)
        result = extract_week_plan("Tenho reunião amanhã", [])
        assert result == []

    def test_invalid_json_returns_empty_list(self, mocker):
        _make_llm_mock(mocker, "invalid json")
        result = extract_week_plan("texto", [])
        assert result == []

    def test_non_list_json_returns_empty_list(self, mocker):
        _make_llm_mock(mocker, '{"key": "value"}')
        result = extract_week_plan("texto", [])
        assert result == []

    def test_invalid_item_skipped(self, mocker):
        payload = json.dumps([{"title": "Sem due_date"}])  # missing required due_date
        _make_llm_mock(mocker, payload)
        result = extract_week_plan("texto", [])
        assert result == []


# ---------------------------------------------------------------------------
# classify_journal_entry
# ---------------------------------------------------------------------------


class TestClassifyJournalEntry:
    def test_returns_dict_with_required_keys(self, mocker):
        _make_llm_mock(mocker, '{"title": "T", "layer": "ego", "tags": []}')
        result = classify_journal_entry("texto")
        assert "title" in result
        assert "layer" in result
        assert "tags" in result

    def test_title_from_llm(self, mocker):
        _make_llm_mock(mocker, '{"title": "Crise às 3h", "layer": "shadow", "tags": ["medo"]}')
        result = classify_journal_entry("texto")
        assert result["title"] == "Crise às 3h"

    def test_layer_from_llm(self, mocker):
        _make_llm_mock(mocker, '{"title": "T", "layer": "shadow", "tags": []}')
        result = classify_journal_entry("texto")
        assert result["layer"] == "shadow"

    def test_tags_list_from_llm(self, mocker):
        _make_llm_mock(mocker, '{"title": "T", "layer": "ego", "tags": ["medo", "clareza"]}')
        result = classify_journal_entry("texto")
        assert result["tags"] == ["medo", "clareza"]

    def test_invalid_json_fallback_uses_content_prefix(self, mocker):
        content = "Entrada de diário muito longa que deve ser truncada no título"
        _make_llm_mock(mocker, "not valid json")
        result = classify_journal_entry(content)
        assert result["title"] == content[:60]

    def test_invalid_json_fallback_layer_is_ego(self, mocker):
        _make_llm_mock(mocker, "not valid json")
        result = classify_journal_entry("texto")
        assert result["layer"] == "ego"

    def test_invalid_json_fallback_tags_is_empty(self, mocker):
        _make_llm_mock(mocker, "not valid json")
        result = classify_journal_entry("texto")
        assert result["tags"] == []

    def test_missing_title_uses_content_prefix(self, mocker):
        content = "Texto sem título no retorno do LLM"
        _make_llm_mock(mocker, '{"layer": "ego", "tags": []}')
        result = classify_journal_entry(content)
        assert result["title"] == content[:60]

    def test_markdown_fencing_cleaned(self, mocker):
        payload = '```json\n{"title": "T", "layer": "self", "tags": ["propósito"]}\n```'
        _make_llm_mock(mocker, payload)
        result = classify_journal_entry("texto")
        assert result["title"] == "T"
        assert result["layer"] == "self"
