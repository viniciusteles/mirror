"""Fixtures compartilhadas para todos os testes."""

import sqlite3
from unittest.mock import MagicMock

import numpy as np
import pytest

from memory.db.schema import SCHEMA


@pytest.fixture
def db_conn():
    """Conexão SQLite em memória com schema completo. Isolada por teste."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA)
    yield conn
    conn.close()


@pytest.fixture
def store(db_conn):
    """Store com banco em memória."""
    from memory.storage.store import Store

    return Store(db_conn)


@pytest.fixture
def mock_embeddings(mocker):
    """Vetor determinístico unitário (1536-dim). Nenhuma chamada à OpenAI.

    Patched at the source module and at each service module that imports generate_embedding
    at the top level (top-level imports create a local binding that must be patched separately).
    """
    vec = np.ones(1536, dtype=np.float32) / np.sqrt(1536)
    mocker.patch("memory.intelligence.embeddings.generate_embedding", return_value=vec)
    mocker.patch("memory.intelligence.search.generate_embedding", return_value=vec)
    mocker.patch("memory.services.memory.generate_embedding", return_value=vec)
    mocker.patch("memory.services.attachment.generate_embedding", return_value=vec)
    mocker.patch("memory.services.conversation.generate_embedding", return_value=vec)
    return vec


@pytest.fixture
def mock_extraction(mocker):
    """Mocka o cliente OpenAI dentro do módulo extraction. Nenhuma chamada a LLM."""
    mock_choice = MagicMock()
    mock_choice.message.content = (
        '[{"title":"Insight de teste","content":"Conteúdo do teste",'
        '"memory_type":"insight","layer":"ego","tags":["teste"]}]'
    )
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    mock_openai_instance = MagicMock()
    mock_openai_instance.chat.completions.create.return_value = mock_completion

    mocker.patch(
        "memory.intelligence.extraction.OpenAI",
        return_value=mock_openai_instance,
    )
    return mock_openai_instance
