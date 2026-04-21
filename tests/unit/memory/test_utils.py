"""Testes unitários para memory.utils."""

import pytest

from memory.utils import strip_accents

pytestmark = pytest.mark.unit


class TestStripAccents:
    def test_removes_acute_accents(self):
        assert strip_accents("episódio") == "episodio"

    def test_removes_grave_accents(self):
        assert strip_accents("pàssaro") == "passaro"

    def test_removes_tilde(self):
        assert strip_accents("ação") == "acao"

    def test_removes_cedilla(self):
        assert strip_accents("coração") == "coracao"

    def test_plain_ascii_unchanged(self):
        assert strip_accents("hello world") == "hello world"

    def test_empty_string(self):
        assert strip_accents("") == ""

    def test_uppercase_accents_removed(self):
        assert strip_accents("AÇÃO") == "ACAO"

    def test_mixed_accented_and_plain(self):
        assert strip_accents("São Paulo") == "Sao Paulo"

    def test_numbers_and_symbols_unchanged(self):
        assert strip_accents("abc123!@#") == "abc123!@#"

    def test_multiple_accent_types(self):
        assert strip_accents("héllo wörld") == "hello world"

    def test_already_clean_string_unchanged(self):
        text = "mirror mind"
        assert strip_accents(text) == text
