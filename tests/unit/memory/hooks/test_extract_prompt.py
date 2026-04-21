import json

from memory.hooks.extract_prompt import extract_prompt


def test_extracts_prompt_from_valid_hook_payload():
    payload = json.dumps({"session_id": "abc", "prompt": "/mm:mirror hello"})

    assert extract_prompt(payload) == "/mm:mirror hello"


def test_returns_empty_string_when_prompt_is_missing():
    payload = json.dumps({"session_id": "abc"})

    assert extract_prompt(payload) == ""


def test_returns_empty_string_for_invalid_json():
    assert extract_prompt("{not json") == ""


def test_returns_empty_string_when_prompt_is_not_text():
    payload = json.dumps({"prompt": ["unexpected", "shape"]})

    assert extract_prompt(payload) == ""
