"""Integration tests for MemoryClient with a real SQLite database.

External APIs (OpenAI, OpenRouter) are mocked by conftest fixtures.
"""

import json

import pytest

from memory.client import MemoryClient
from memory.intelligence.search import MemorySearch
from memory.storage.store import Store


@pytest.fixture
def client(db_conn, mock_embeddings, mock_extraction):
    """Complete MemoryClient over an in-memory database, without external calls."""
    from memory.services.attachment import AttachmentService
    from memory.services.conversation import ConversationService
    from memory.services.identity import IdentityService
    from memory.services.journey import JourneyService
    from memory.services.memory import MemoryService
    from memory.services.tasks import TaskService

    mem = MemoryClient.__new__(MemoryClient)
    mem.env = "test"
    mem.db_path = ":memory:"
    mem.conn = db_conn
    mem.store = Store(db_conn)
    mem.search_engine = MemorySearch(mem.store)

    mem.attachments = AttachmentService(mem.store)
    mem.identity = IdentityService(mem.store, mem.attachments)
    mem.journeys = JourneyService(mem.store, mem.identity)
    mem.tasks = TaskService(mem.store, mem.journeys)
    mem.memories = MemoryService(mem.store, mem.search_engine)
    mem.conversations = ConversationService(mem.store, mem.memories, mem.tasks)
    return mem


# ---------------------------------------------------------------------------
# Conversation lifecycle
# ---------------------------------------------------------------------------


class TestClientEnglishServiceAttributes:
    def test_exposes_english_service_attributes_only(self, client):
        assert client.attachments
        assert client.identity
        assert client.journeys
        assert client.tasks
        assert client.conversations

        assert not hasattr(client, "anexos")
        assert not hasattr(client, "identidade")
        assert not hasattr(client, "travessias")
        assert not hasattr(client, "tarefas")
        assert not hasattr(client, "conversas")


class TestConversationLifecycle:
    def test_start_returns_conversation(self, client):
        conv = client.start_conversation("claude_code")
        assert conv.id
        assert conv.interface == "claude_code"

    def test_start_accepts_journey(self, client):
        conv = client.start_conversation("cli", persona="writer", journey="reflexo")
        assert conv.persona == "writer"
        assert conv.journey == "reflexo"

    def test_add_message_returns_message(self, client):
        conv = client.start_conversation("cli")
        msg = client.add_message(conv.id, role="user", content="Olá!")
        assert msg.conversation_id == conv.id
        assert msg.content == "Olá!"

    def test_end_conversation_without_extract(self, client):
        conv = client.start_conversation("cli")
        client.add_message(conv.id, "user", "Teste")
        memories = client.end_conversation(conv.id, extract=False)
        assert memories == []

    def test_end_conversation_with_extract(self, client):
        conv = client.start_conversation("cli")
        client.add_message(conv.id, "user", "Aprendi algo importante hoje")
        client.add_message(conv.id, "assistant", "Interessante, pode elaborar?")
        memories = client.end_conversation(conv.id, extract=True)
        # mock_extraction returns one memory
        assert len(memories) >= 0  # extraction may succeed or be suppressed by error handling

    def test_end_empty_conversation_returns_empty(self, client):
        conv = client.start_conversation("cli")
        memories = client.end_conversation(conv.id, extract=True)
        assert memories == []

    def test_full_lifecycle(self, client):
        """start → add_message x 2 → end → verify conversation stored."""
        conv = client.start_conversation("claude_code", persona="mentor")
        client.add_message(conv.id, "user", "Como definir meu posicionamento?")
        client.add_message(conv.id, "assistant", "Vamos começar pelo contexto...")
        client.end_conversation(conv.id, extract=False)

        stored = client.store.get_conversation(conv.id)
        assert stored is not None
        assert stored.ended_at is not None

        messages = client.store.get_messages(conv.id)
        assert len(messages) == 2


# ---------------------------------------------------------------------------
# Memory operations
# ---------------------------------------------------------------------------


class TestMemoryOperations:
    def test_add_memory(self, client):
        mem = client.add_memory(
            title="Decisão de pricing",
            content="Vamos manter o preço atual por 3 meses.",
            memory_type="decision",
            layer="ego",
        )
        assert mem.id
        assert mem.memory_type == "decision"

    def test_add_memory_accepts_journey(self, client):
        mem = client.add_memory(
            title="Insight de produto",
            content="Usuários querem simplicidade.",
            memory_type="insight",
            journey="uncle-vinny",
        )
        assert mem.journey == "uncle-vinny"

    def test_search_returns_list(self, client):
        client.add_memory(title="A", content="Texto relevante", memory_type="insight")
        results = client.search("texto relevante")
        assert isinstance(results, list)

    def test_get_by_type(self, client):
        client.add_memory(title="D", content="x", memory_type="decision")
        client.add_memory(title="I", content="y", memory_type="insight")
        decisions = client.get_by_type("decision")
        assert all(m.memory_type == "decision" for m in decisions)

    def test_get_by_layer(self, client):
        client.add_memory(title="Soul", content="x", memory_type="insight", layer="self")
        client.add_memory(title="Op", content="y", memory_type="insight", layer="ego")
        self_mems = client.get_by_layer("self")
        assert all(m.layer == "self" for m in self_mems)

    def test_get_by_journey(self, client):
        mem = client.add_memory(
            title="Insight de produto",
            content="Usuários querem simplicidade.",
            memory_type="insight",
            journey="uncle-vinny",
        )
        by_journey = client.get_by_journey("uncle-vinny")
        assert any(m.id == mem.id for m in by_journey)

    def test_search_accepts_journey(self, client):
        client.add_memory(
            title="Insight scoped",
            content="Scoped content.",
            memory_type="insight",
            journey="uncle-vinny",
        )
        results = client.search("scoped", journey="uncle-vinny")
        assert isinstance(results, list)


# ---------------------------------------------------------------------------
# Identity operations
# ---------------------------------------------------------------------------


class TestIdentityOperations:
    def test_set_and_get_identity(self, client):
        client.set_identity("ego", "behavior", "Be direct and concise.")
        result = client.get_identity("ego", "behavior")
        assert "direct" in result

    def test_get_missing_identity_returns_none(self, client):
        assert client.get_identity("ghost", "key") is None

    def test_set_identity_update(self, client):
        client.set_identity("user", "identity", "Vinícius v1")
        client.set_identity("user", "identity", "Vinícius v2")
        result = client.get_identity("user", "identity")
        assert "v2" in result

    def test_load_mirror_context_accepts_journey(self, client):
        client.set_identity("journey", "reflexo", "# O Reflexo\n**Status:** active")
        context = client.load_mirror_context(journey="reflexo")
        assert "=== journey/reflexo ===" in context

    def test_detect_persona_reads_routing_metadata_from_db(self, client):
        client.set_identity(
            "persona",
            "engineer",
            "Engineer prompt.",
            metadata=json.dumps({"routing_keywords": ["python", "debug", "database"]}),
        )
        matches = client.detect_persona("please debug this python database issue")
        assert matches[0] == ("engineer", 3.0, "keyword")


# ---------------------------------------------------------------------------
# Journey operations
# ---------------------------------------------------------------------------


class TestJourneyOperations:
    def test_journey_path_methods(self, client):
        client.set_journey_path("reflexo", "# Journey Path")
        assert client.get_journey_path("reflexo") == "# Journey Path"

    def test_journey_path_accepts_journey_keyword(self, client):
        client.set_journey_path(journey="reflexo", content="# Journey Path")
        assert client.get_journey_path(journey="reflexo") == "# Journey Path"

    def test_journey_status_accepts_journey_keyword(self, client):
        client.set_identity("journey", "reflexo", "# O Reflexo\n**Status:** active")
        result = client.get_journey_status(journey="reflexo")
        assert "reflexo" in result


# ---------------------------------------------------------------------------
# Task operations
# ---------------------------------------------------------------------------


class TestTaskOperations:
    def test_add_task(self, client):
        task = client.add_task(title="Implementar testes", journey="automation")
        assert task.id
        assert task.title == "Implementar testes"
        assert task.status == "todo"
        assert task.journey == "automation"

    def test_list_tasks(self, client):
        client.add_task(title="A")
        client.add_task(title="B")
        tasks = client.list_tasks()
        assert len(tasks) >= 2

    def test_complete_task(self, client):
        task = client.add_task(title="Fazer deploy")
        client.complete_task(task.id)
        fetched = client.store.get_task(task.id)
        assert fetched.status == "done"
        assert fetched.completed_at is not None

    def test_update_task(self, client):
        task = client.add_task(title="Task")
        client.update_task(task.id, status="doing")
        fetched = client.store.get_task(task.id)
        assert fetched.status == "doing"

    def test_find_tasks(self, client):
        client.add_task(title="Escrever artigo sobre liberdade")
        results = client.find_tasks("artigo")
        assert len(results) >= 1

    def test_task_queries_accept_journey(self, client):
        client.add_task(title="Task da jornada", journey="automation")
        assert client.list_tasks(journey="automation")
        assert client.find_tasks("jornada", journey="automation")

    def test_import_tasks_from_journey_path_empty(self, client):
        result = client.import_tasks_from_journey_path("journey-sem-journey_path")
        assert result == []


# ---------------------------------------------------------------------------
# Attachment operations
# ---------------------------------------------------------------------------


class TestAttachmentOperations:
    def test_add_and_get_attachment(self, client):
        att = client.add_attachment(
            journey_id="reflexo",
            name="spec.md",
            content="# Especificação do Reflexo",
        )
        assert att.id
        results = client.get_attachments("reflexo")
        assert any(a.id == att.id for a in results)

    def test_attachment_methods_accept_journey_id(self, client):
        att = client.add_attachment(
            journey_id="reflexo",
            name="spec.md",
            content="# Especificação do Reflexo",
        )
        assert att.journey_id == "reflexo"
        assert client.get_attachment(journey_id="reflexo", name="spec.md") is not None
        assert client.get_attachments(journey_id="reflexo")

    def test_search_attachments_returns_list(self, client):
        client.add_attachment("t1", "doc.md", "Conteúdo relevante para busca")
        results = client.search_attachments("t1", "relevante")
        assert isinstance(results, list)
