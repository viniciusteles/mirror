"""Shared fixtures for service-layer tests."""

import numpy as np
import pytest


@pytest.fixture
def emb_vec():
    """Deterministic embedding vector matching the root conftest pattern."""
    return np.ones(1536, dtype=np.float32) / np.sqrt(1536)


# --- Embedding patches by service module ---


@pytest.fixture
def mock_memory_embedding(mocker, emb_vec):
    """Mocks generate_embedding in the memory.py and search.py namespaces."""
    mocker.patch("memory.services.memory.generate_embedding", return_value=emb_vec)
    mocker.patch("memory.intelligence.search.generate_embedding", return_value=emb_vec)
    return emb_vec


@pytest.fixture
def mock_attachment_embedding(mocker, emb_vec):
    """Mocks generate_embedding in the attachment.py namespace."""
    mocker.patch("memory.services.attachment.generate_embedding", return_value=emb_vec)
    return emb_vec


@pytest.fixture
def mock_conversation_embedding(mocker, emb_vec):
    """Mocks generate_embedding in the conversation.py and memory.py namespaces.

    end_conversation calls self.memories.add_memory(), which uses the memory.py namespace.
    """
    mocker.patch("memory.services.conversation.generate_embedding", return_value=emb_vec)
    mocker.patch("memory.services.memory.generate_embedding", return_value=emb_vec)
    mocker.patch("memory.intelligence.search.generate_embedding", return_value=emb_vec)
    return emb_vec


# --- LLM extraction patches ---


@pytest.fixture
def mock_classify_journal(mocker):
    """Mocks classify_journal_entry at the source; memory.py imports it lazily."""
    mocker.patch(
        "memory.intelligence.extraction.classify_journal_entry",
        return_value={"title": "Entrada Classificada", "layer": "ego", "tags": ["reflexao"]},
    )


@pytest.fixture
def mock_extract_memories(mocker):
    """Mocks extract_memories in the conversation.py namespace."""
    from memory.models import ExtractedMemory

    mocker.patch(
        "memory.services.conversation.extract_memories",
        return_value=[
            ExtractedMemory(
                title="Insight de teste",
                content="Conteúdo extraído",
                memory_type="insight",
                layer="ego",
            )
        ],
    )


@pytest.fixture
def mock_extract_tasks(mocker):
    """Mocks extract_tasks in the conversation.py namespace."""
    mocker.patch("memory.services.conversation.extract_tasks", return_value=[])


@pytest.fixture
def mock_extract_week_plan(mocker):
    """Mocks extract_week_plan at the source; tasks.py imports it lazily."""
    from memory.models import ExtractedWeekItem

    mocker.patch(
        "memory.intelligence.extraction.extract_week_plan",
        return_value=[
            ExtractedWeekItem(title="Task planejada", due_date="2026-04-14"),
        ],
    )


# --- Service instances, built bottom-up like client.py ---


@pytest.fixture
def attachment_service(store):
    from memory.services.attachment import AttachmentService

    return AttachmentService(store)


@pytest.fixture
def identity_service(store, attachment_service):
    from memory.services.identity import IdentityService

    return IdentityService(store, attachments=attachment_service)


@pytest.fixture
def journey_service(store, identity_service):
    from memory.services.journey import JourneyService

    return JourneyService(store, identity=identity_service)


@pytest.fixture
def memory_service(store):
    from memory.intelligence.search import MemorySearch
    from memory.services.memory import MemoryService

    return MemoryService(store, search_engine=MemorySearch(store))


@pytest.fixture
def task_service(store, journey_service):
    from memory.services.tasks import TaskService

    return TaskService(store, journeys=journey_service)


@pytest.fixture
def conversation_service(store, memory_service, task_service):
    from memory.services.conversation import ConversationService

    return ConversationService(store, memories=memory_service, tasks=task_service)
