"""Unit tests for memory.intelligence.extraction."""

import json
from unittest.mock import MagicMock

import pytest

from memory.intelligence.extraction import (
    _parse_json_response,
    classify_journal_entry,
    curate_against_existing,
    extract_memories,
    extract_tasks,
    extract_week_plan,
    format_transcript,
)
from memory.intelligence.llm_router import LLMResponse
from memory.models import ExtractedMemory, ExtractedTask, ExtractedWeekItem, Memory, Message

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


def _make_send_to_model_mock(mocker, content: str) -> MagicMock:
    """Patch extraction.send_to_model to return `content` as the LLM response."""
    mock_response = LLMResponse(
        model="google/gemini-2.5-flash-lite",
        content=content,
        prompt_tokens=10,
        completion_tokens=5,
        latency_ms=100,
        prompt="[mocked prompt]",
    )
    return mocker.patch("memory.intelligence.extraction.send_to_model", return_value=mock_response)


# ---------------------------------------------------------------------------
# _parse_json_response
# ---------------------------------------------------------------------------


class TestParseJsonResponse:
    def test_parses_clean_json_list(self):
        assert _parse_json_response("[1, 2, 3]") == [1, 2, 3]

    def test_parses_clean_json_dict(self):
        assert _parse_json_response('{"a": 1}') == {"a": 1}

    def test_strips_markdown_fencing(self):
        raw = '```json\n[{"x": 1}]\n```'
        assert _parse_json_response(raw) == [{"x": 1}]

    def test_strips_fencing_without_language_tag(self):
        raw = '```\n{"a": 1}\n```'
        assert _parse_json_response(raw) == {"a": 1}

    def test_returns_none_for_invalid_json(self):
        assert _parse_json_response("not json at all") is None

    def test_returns_none_for_empty_string(self):
        assert _parse_json_response("") is None

    def test_returns_none_for_whitespace_only(self):
        assert _parse_json_response("   ") is None


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
        result = format_transcript(msgs, user_name="Alice")
        assert result == "**Alice:** Question"

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
        _make_send_to_model_mock(mocker, payload)
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
        _make_send_to_model_mock(mocker, payload)
        result = extract_memories(sample_messages)
        assert result[0].title == "Tít"
        assert result[0].content == "Cont"
        assert result[0].memory_type == "decision"
        assert result[0].layer == "self"
        assert result[0].tags == ["a"]

    def test_invalid_json_returns_empty_list(self, mocker, sample_messages):
        _make_send_to_model_mock(mocker, "not valid json")
        result = extract_memories(sample_messages)
        assert result == []

    def test_non_list_json_returns_empty_list(self, mocker, sample_messages):
        _make_send_to_model_mock(mocker, '{"key": "value"}')
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
        _make_send_to_model_mock(mocker, payload)
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
        _make_send_to_model_mock(mocker, payload)
        result = extract_memories(sample_messages)
        assert len(result) == 1
        assert result[0].title == "Valid"

    def test_persona_injected_when_llm_omits_it(self, mocker, sample_messages):
        payload = json.dumps(
            [{"title": "T", "content": "C", "memory_type": "insight", "layer": "ego", "tags": []}]
        )
        _make_send_to_model_mock(mocker, payload)
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
        _make_send_to_model_mock(mocker, payload)
        result = extract_memories(sample_messages, persona="mentor")
        assert result[0].persona == "writer"

    def test_journey_injected_when_missing(self, mocker, sample_messages):
        payload = json.dumps(
            [{"title": "T", "content": "C", "memory_type": "insight", "layer": "ego", "tags": []}]
        )
        _make_send_to_model_mock(mocker, payload)
        result = extract_memories(sample_messages, journey="mirror")
        assert result[0].journey == "mirror"

    def test_journey_not_overwritten(self, mocker, sample_messages):
        payload = json.dumps(
            [
                {
                    "title": "T",
                    "content": "C",
                    "memory_type": "insight",
                    "layer": "ego",
                    "tags": [],
                    "journey": "other",
                }
            ]
        )
        _make_send_to_model_mock(mocker, payload)
        result = extract_memories(sample_messages, journey="mirror")
        assert result[0].journey == "other"

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
        _make_send_to_model_mock(mocker, payload)
        result = extract_memories(sample_messages)
        assert result == []

    def test_on_llm_call_invoked_with_response(self, mocker, sample_messages):
        _make_send_to_model_mock(mocker, "[]")
        callback = MagicMock()
        extract_memories(sample_messages, on_llm_call=callback)
        callback.assert_called_once()
        assert isinstance(callback.call_args[0][0], LLMResponse)

    def test_on_llm_call_not_invoked_when_none(self, mocker, sample_messages):
        _make_send_to_model_mock(mocker, "[]")
        # Should not raise even with no callback
        result = extract_memories(sample_messages, on_llm_call=None)
        assert result == []

    def test_on_llm_call_skipped_for_empty_messages(self):
        callback = MagicMock()
        extract_memories([], on_llm_call=callback)
        callback.assert_not_called()

    def test_prompt_contains_english_journey_key(self, mocker, sample_messages):
        mock_send = _make_send_to_model_mock(mocker, "[]")
        extract_memories(sample_messages)
        messages_arg = mock_send.call_args[0][1]
        prompt_content = messages_arg[0]["content"]
        assert '"journey"' in prompt_content
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
                    "title": "Do X",
                    "due_date": "2026-04-15",
                    "journey": None,
                    "stage": None,
                    "context": "ctx",
                }
            ]
        )
        _make_send_to_model_mock(mocker, payload)
        result = extract_tasks(sample_messages)
        assert len(result) == 1
        assert isinstance(result[0], ExtractedTask)

    def test_title_field_mapped(self, mocker, sample_messages):
        payload = json.dumps(
            [{"title": "Do X", "due_date": None, "journey": None, "stage": None, "context": None}]
        )
        _make_send_to_model_mock(mocker, payload)
        result = extract_tasks(sample_messages)
        assert result[0].title == "Do X"

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
        _make_send_to_model_mock(mocker, payload)
        result = extract_tasks(sample_messages)
        assert result[0].due_date == "2026-04-15"

    def test_journey_fallback_from_argument(self, mocker, sample_messages):
        payload = json.dumps(
            [{"title": "T", "due_date": None, "journey": None, "stage": None, "context": None}]
        )
        _make_send_to_model_mock(mocker, payload)
        result = extract_tasks(sample_messages, journey="mirror")
        assert result[0].journey == "mirror"

    def test_accepts_english_journey_from_llm(self, mocker, sample_messages):
        payload = json.dumps(
            [
                {
                    "title": "Do X",
                    "due_date": None,
                    "journey": "mirror",
                    "stage": None,
                    "context": None,
                }
            ]
        )
        _make_send_to_model_mock(mocker, payload)
        result = extract_tasks(sample_messages)
        assert result[0].journey == "mirror"

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
        _make_send_to_model_mock(mocker, payload)
        result = extract_tasks(sample_messages)
        assert result[0].journey is None

    def test_invalid_json_returns_empty_list(self, mocker, sample_messages):
        _make_send_to_model_mock(mocker, "garbage")
        result = extract_tasks(sample_messages)
        assert result == []

    def test_item_missing_title_skipped(self, mocker, sample_messages):
        payload = json.dumps([{"due_date": "2026-04-15"}])  # no title
        _make_send_to_model_mock(mocker, payload)
        result = extract_tasks(sample_messages)
        assert result == []

    def test_markdown_fencing_cleaned(self, mocker, sample_messages):
        payload = (
            "```json\n"
            + json.dumps(
                [{"title": "T", "due_date": None, "journey": None, "stage": None, "context": None}]
            )
            + "\n```"
        )
        _make_send_to_model_mock(mocker, payload)
        result = extract_tasks(sample_messages)
        assert len(result) == 1

    def test_on_llm_call_invoked_with_response(self, mocker, sample_messages):
        _make_send_to_model_mock(mocker, "[]")
        callback = MagicMock()
        extract_tasks(sample_messages, on_llm_call=callback)
        callback.assert_called_once()
        assert isinstance(callback.call_args[0][0], LLMResponse)

    def test_on_llm_call_not_invoked_when_none(self, mocker, sample_messages):
        _make_send_to_model_mock(mocker, "[]")
        result = extract_tasks(sample_messages, on_llm_call=None)
        assert result == []

    def test_prompt_contains_english_journey_key(self, mocker, sample_messages):
        mock_send = _make_send_to_model_mock(mocker, "[]")
        extract_tasks(sample_messages)
        messages_arg = mock_send.call_args[0][1]
        prompt_content = messages_arg[0]["content"]
        assert '"journey": "slug" or null' in prompt_content
        assert '"travessia"' not in prompt_content


# ---------------------------------------------------------------------------
# extract_week_plan
# ---------------------------------------------------------------------------


class TestExtractWeekPlan:
    def test_returns_extracted_week_items(self, mocker):
        payload = json.dumps(
            [
                {
                    "title": "Meeting",
                    "due_date": "2026-04-14",
                    "scheduled_at": None,
                    "time_hint": None,
                    "journey": None,
                    "context": "",
                }
            ]
        )
        _make_send_to_model_mock(mocker, payload)
        result = extract_week_plan("I have a meeting tomorrow", [])
        assert len(result) == 1
        assert isinstance(result[0], ExtractedWeekItem)

    def test_today_injected_into_prompt(self, mocker):
        import re

        mock_send = _make_send_to_model_mock(mocker, "[]")
        extract_week_plan("text", [])
        messages_arg = mock_send.call_args[0][1]
        prompt_content = messages_arg[0]["content"]
        assert re.search(r"\d{4}-\d{2}-\d{2}", prompt_content)

    def test_weekday_english_name_in_prompt(self, mocker):
        mock_send = _make_send_to_model_mock(mocker, "[]")
        extract_week_plan("text", [])
        messages_arg = mock_send.call_args[0][1]
        prompt_content = messages_arg[0]["content"]
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        assert any(day in prompt_content for day in weekdays)

    def test_journey_context_formatted_in_prompt(self, mocker):
        mock_send = _make_send_to_model_mock(mocker, "[]")
        extract_week_plan("text", [{"slug": "mirror", "description": "mirror project"}])
        messages_arg = mock_send.call_args[0][1]
        prompt_content = messages_arg[0]["content"]
        assert "mirror" in prompt_content

    def test_empty_journey_context_shows_fallback(self, mocker):
        mock_send = _make_send_to_model_mock(mocker, "[]")
        extract_week_plan("text", [])
        messages_arg = mock_send.call_args[0][1]
        prompt_content = messages_arg[0]["content"]
        assert "no active journeys" in prompt_content

    def test_week_plan_prompt_requests_english_journey_key(self, mocker):
        mock_send = _make_send_to_model_mock(mocker, "[]")
        extract_week_plan("text", [])
        messages_arg = mock_send.call_args[0][1]
        prompt_content = messages_arg[0]["content"]
        assert '"journey": "slug" or null' in prompt_content
        assert '"travessia"' not in prompt_content

    def test_stale_llm_journey_key_is_rejected(self, mocker):
        payload = json.dumps(
            [
                {
                    "title": "Meeting",
                    "due_date": "2026-04-14",
                    "scheduled_at": None,
                    "time_hint": None,
                    "travessia": "legacy",
                    "context": "",
                }
            ]
        )
        _make_send_to_model_mock(mocker, payload)
        result = extract_week_plan("I have a meeting tomorrow", [])
        assert result == []

    def test_invalid_json_returns_empty_list(self, mocker):
        _make_send_to_model_mock(mocker, "invalid json")
        result = extract_week_plan("text", [])
        assert result == []

    def test_non_list_json_returns_empty_list(self, mocker):
        _make_send_to_model_mock(mocker, '{"key": "value"}')
        result = extract_week_plan("text", [])
        assert result == []

    def test_invalid_item_skipped(self, mocker):
        payload = json.dumps([{"title": "No due_date"}])  # missing required due_date
        _make_send_to_model_mock(mocker, payload)
        result = extract_week_plan("text", [])
        assert result == []

    def test_on_llm_call_invoked_with_response(self, mocker):
        _make_send_to_model_mock(mocker, "[]")
        callback = MagicMock()
        extract_week_plan("text", [], on_llm_call=callback)
        callback.assert_called_once()
        assert isinstance(callback.call_args[0][0], LLMResponse)

    def test_on_llm_call_not_invoked_when_none(self, mocker):
        _make_send_to_model_mock(mocker, "[]")
        result = extract_week_plan("text", [], on_llm_call=None)
        assert result == []


# ---------------------------------------------------------------------------
# classify_journal_entry
# ---------------------------------------------------------------------------


class TestClassifyJournalEntry:
    def test_returns_dict_with_required_keys(self, mocker):
        _make_send_to_model_mock(mocker, '{"title": "T", "layer": "ego", "tags": []}')
        result = classify_journal_entry("text")
        assert "title" in result
        assert "layer" in result
        assert "tags" in result

    def test_title_from_llm(self, mocker):
        _make_send_to_model_mock(
            mocker, '{"title": "Crisis at 3am", "layer": "shadow", "tags": ["fear"]}'
        )
        result = classify_journal_entry("text")
        assert result["title"] == "Crisis at 3am"

    def test_layer_from_llm(self, mocker):
        _make_send_to_model_mock(mocker, '{"title": "T", "layer": "shadow", "tags": []}')
        result = classify_journal_entry("text")
        assert result["layer"] == "shadow"

    def test_tags_list_from_llm(self, mocker):
        _make_send_to_model_mock(
            mocker, '{"title": "T", "layer": "ego", "tags": ["fear", "clarity"]}'
        )
        result = classify_journal_entry("text")
        assert result["tags"] == ["fear", "clarity"]

    def test_invalid_json_fallback_uses_content_prefix(self, mocker):
        content = "A long journal entry that should be truncated in the title fallback"
        _make_send_to_model_mock(mocker, "not valid json")
        result = classify_journal_entry(content)
        assert result["title"] == content[:60]

    def test_invalid_json_fallback_layer_is_ego(self, mocker):
        _make_send_to_model_mock(mocker, "not valid json")
        result = classify_journal_entry("text")
        assert result["layer"] == "ego"

    def test_invalid_json_fallback_tags_is_empty(self, mocker):
        _make_send_to_model_mock(mocker, "not valid json")
        result = classify_journal_entry("text")
        assert result["tags"] == []

    def test_missing_title_uses_content_prefix(self, mocker):
        content = "Text without title in LLM response"
        _make_send_to_model_mock(mocker, '{"layer": "ego", "tags": []}')
        result = classify_journal_entry(content)
        assert result["title"] == content[:60]

    def test_markdown_fencing_cleaned(self, mocker):
        payload = '```json\n{"title": "T", "layer": "self", "tags": ["purpose"]}\n```'
        _make_send_to_model_mock(mocker, payload)
        result = classify_journal_entry("text")
        assert result["title"] == "T"
        assert result["layer"] == "self"

    def test_on_llm_call_invoked_with_response(self, mocker):
        _make_send_to_model_mock(mocker, '{"title": "T", "layer": "ego", "tags": []}')
        callback = MagicMock()
        classify_journal_entry("text", on_llm_call=callback)
        callback.assert_called_once()
        assert isinstance(callback.call_args[0][0], LLMResponse)

    def test_on_llm_call_not_invoked_when_none(self, mocker):
        _make_send_to_model_mock(mocker, '{"title": "T", "layer": "ego", "tags": []}')
        result = classify_journal_entry("text", on_llm_call=None)
        assert result["title"] == "T"


# ---------------------------------------------------------------------------
# curate_against_existing
# ---------------------------------------------------------------------------


def _make_candidate(**kwargs) -> ExtractedMemory:
    defaults: dict = {
        "title": "Some Insight",
        "content": "Something was learned.",
        "memory_type": "insight",
        "layer": "ego",
        "tags": [],
    }
    defaults.update(kwargs)
    return ExtractedMemory(**defaults)


def _make_existing(**kwargs) -> Memory:
    defaults: dict = {
        "memory_type": "insight",
        "layer": "ego",
        "title": "Old Insight",
        "content": "Something already known.",
    }
    defaults.update(kwargs)
    return Memory(**defaults)


class TestCurateAgainstExisting:
    def test_empty_candidates_returns_empty_without_llm_call(self, mocker):
        mock_send = mocker.patch("memory.intelligence.extraction.send_to_model")
        result = curate_against_existing([], [_make_existing()])
        assert result == []
        mock_send.assert_not_called()

    def test_empty_existing_returns_candidates_without_llm_call(self, mocker):
        mock_send = mocker.patch("memory.intelligence.extraction.send_to_model")
        candidates = [_make_candidate()]
        result = curate_against_existing(candidates, [])
        assert result == candidates
        mock_send.assert_not_called()

    def test_valid_response_returns_curated_list(self, mocker):
        payload = json.dumps(
            [
                {
                    "title": "Kept",
                    "content": "Novel.",
                    "memory_type": "decision",
                    "layer": "ego",
                    "tags": [],
                }
            ]
        )
        _make_send_to_model_mock(mocker, payload)
        candidates = [_make_candidate(title="Kept"), _make_candidate(title="Dropped")]
        result = curate_against_existing(candidates, [_make_existing()])
        assert len(result) == 1
        assert result[0].title == "Kept"

    def test_all_dropped_returns_empty_list(self, mocker):
        _make_send_to_model_mock(mocker, "[]")
        candidates = [_make_candidate()]
        result = curate_against_existing(candidates, [_make_existing()])
        assert result == []

    def test_malformed_json_fails_open(self, mocker):
        _make_send_to_model_mock(mocker, "not valid json")
        candidates = [_make_candidate()]
        result = curate_against_existing(candidates, [_make_existing()])
        assert result == candidates

    def test_non_list_json_fails_open(self, mocker):
        _make_send_to_model_mock(mocker, '{"oops": true}')
        candidates = [_make_candidate()]
        result = curate_against_existing(candidates, [_make_existing()])
        assert result == candidates

    def test_llm_exception_fails_open(self, mocker):
        mocker.patch(
            "memory.intelligence.extraction.send_to_model", side_effect=RuntimeError("timeout")
        )
        candidates = [_make_candidate()]
        result = curate_against_existing(candidates, [_make_existing()])
        assert result == candidates

    def test_on_llm_call_invoked_when_llm_runs(self, mocker):
        _make_send_to_model_mock(mocker, "[]")
        callback = MagicMock()
        curate_against_existing([_make_candidate()], [_make_existing()], on_llm_call=callback)
        callback.assert_called_once()
        assert isinstance(callback.call_args[0][0], LLMResponse)

    def test_on_llm_call_not_invoked_when_existing_empty(self, mocker):
        mock_send = mocker.patch("memory.intelligence.extraction.send_to_model")
        callback = MagicMock()
        curate_against_existing([_make_candidate()], [], on_llm_call=callback)
        mock_send.assert_not_called()
        callback.assert_not_called()
