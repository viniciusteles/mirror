"""Utilitários compartilhados do módulo memory."""

import unicodedata


def strip_accents(s: str) -> str:
    """Remove acentos para comparação textual (ex: 'episódio' → 'episodio')."""
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
