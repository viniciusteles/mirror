"""Unit tests for ConversationService."""

from memory.models import Conversation, Message


class TestConversationServiceStartConversation:
    def test_returns_conversation_object(self, conversation_service):
        conv = conversation_service.start_conversation(interface="claude_code")
        assert isinstance(conv, Conversation)
        assert conv.interface == "claude_code"

    def test_persisted_in_store(self, conversation_service, store):
        conv = conversation_service.start_conversation(interface="cli")
        stored = store.get_conversation(conv.id)
        assert stored is not None
        assert stored.id == conv.id

    def test_optional_fields_preserved(self, conversation_service, store):
        conv = conversation_service.start_conversation(
            interface="django",
            persona="writer",
            journey="reflexo",
            title="Conversa sobre o artigo",
        )
        stored = store.get_conversation(conv.id)
        assert stored.persona == "writer"
        assert stored.journey == "reflexo"
        assert stored.title == "Conversa sobre o artigo"

    def test_ended_at_initially_none(self, conversation_service, store):
        conv = conversation_service.start_conversation(interface="cli")
        stored = store.get_conversation(conv.id)
        assert stored.ended_at is None


class TestConversationServiceAddMessage:
    def test_returns_message_object(self, conversation_service):
        conv = conversation_service.start_conversation(interface="cli")
        msg = conversation_service.add_message(conv.id, role="user", content="Olá!")
        assert isinstance(msg, Message)
        assert msg.content == "Olá!"
        assert msg.role == "user"

    def test_message_associated_to_conversation(self, conversation_service):
        conv = conversation_service.start_conversation(interface="cli")
        msg = conversation_service.add_message(conv.id, role="user", content="X")
        assert msg.conversation_id == conv.id

    def test_message_persisted(self, conversation_service, store):
        conv = conversation_service.start_conversation(interface="cli")
        conversation_service.add_message(conv.id, role="user", content="Mensagem")
        messages = store.get_messages(conv.id)
        assert len(messages) == 1
        assert messages[0].content == "Mensagem"

    def test_token_count_preserved(self, conversation_service, store):
        conv = conversation_service.start_conversation(interface="cli")
        conversation_service.add_message(
            conv.id, role="assistant", content="Resposta.", token_count=42
        )
        messages = store.get_messages(conv.id)
        assert messages[0].token_count == 42

    def test_multiple_messages_ordered(self, conversation_service, store):
        conv = conversation_service.start_conversation(interface="cli")
        conversation_service.add_message(conv.id, role="user", content="Primeira")
        conversation_service.add_message(conv.id, role="assistant", content="Segunda")
        messages = store.get_messages(conv.id)
        assert messages[0].content == "Primeira"
        assert messages[1].content == "Segunda"


class TestConversationServiceEndConversation:
    def test_extract_false_returns_empty_list(self, conversation_service):
        conv = conversation_service.start_conversation(interface="cli")
        result = conversation_service.end_conversation(conv.id, extract=False)
        assert result == []

    def test_extract_false_marks_ended_at(self, conversation_service, store):
        conv = conversation_service.start_conversation(interface="cli")
        conversation_service.end_conversation(conv.id, extract=False)
        stored = store.get_conversation(conv.id)
        assert stored.ended_at is not None

    def test_empty_messages_returns_empty_list(
        self, conversation_service, mock_conversation_embedding
    ):
        conv = conversation_service.start_conversation(interface="cli")
        result = conversation_service.end_conversation(conv.id, extract=True)
        assert result == []

    def test_memories_extracted_and_stored(
        self,
        conversation_service,
        store,
        mock_conversation_embedding,
        mock_extract_memories,
        mock_extract_tasks,
    ):
        conv = conversation_service.start_conversation(interface="cli", journey="test")
        for i in range(4):
            conversation_service.add_message(conv.id, role="user", content=f"Mensagem {i}")
        result = conversation_service.end_conversation(conv.id)
        assert len(result) == 1
        assert result[0].title == "Insight de teste"
        assert result[0].memory_type == "insight"

    def test_memories_persisted_in_store(
        self,
        conversation_service,
        store,
        mock_conversation_embedding,
        mock_extract_memories,
        mock_extract_tasks,
    ):
        conv = conversation_service.start_conversation(interface="cli", journey="test")
        for i in range(4):
            conversation_service.add_message(conv.id, role="user", content=f"Mensagem {i}")
        result = conversation_service.end_conversation(conv.id)
        stored = store.get_memory(result[0].id)
        assert stored is not None

    def test_embedding_generated_and_stored(
        self,
        conversation_service,
        store,
        mock_extract_memories,
        mock_extract_tasks,
        mocker,
        emb_vec,
    ):
        mock_emb = mocker.patch(
            "memory.services.conversation.generate_embedding", return_value=emb_vec
        )
        mocker.patch("memory.services.memory.generate_embedding", return_value=emb_vec)
        conv = conversation_service.start_conversation(interface="cli", journey="test")
        for i in range(4):
            conversation_service.add_message(conv.id, role="user", content=f"Mensagem {i}")
        conversation_service.end_conversation(conv.id)
        mock_emb.assert_called()

    def test_summary_stored_in_conversation(
        self,
        conversation_service,
        store,
        mock_conversation_embedding,
        mock_extract_memories,
        mock_extract_tasks,
    ):
        conv = conversation_service.start_conversation(interface="cli", journey="test")
        for i in range(4):
            conversation_service.add_message(conv.id, role="user", content=f"Mensagem {i}")
        conversation_service.end_conversation(conv.id)
        stored = store.get_conversation(conv.id)
        assert stored.summary is not None
        assert len(stored.summary) > 0

    def test_task_extraction_called(
        self,
        conversation_service,
        mock_conversation_embedding,
        mock_extract_memories,
        mocker,
    ):
        mock_tasks = mocker.patch("memory.services.conversation.extract_tasks", return_value=[])
        conv = conversation_service.start_conversation(interface="cli", journey="test")
        for i in range(4):
            conversation_service.add_message(conv.id, role="user", content=f"Mensagem {i}")
        conversation_service.end_conversation(conv.id)
        mock_tasks.assert_called_once()

    def test_task_created_when_not_duplicate(
        self,
        conversation_service,
        store,
        mock_conversation_embedding,
        mock_extract_memories,
        mocker,
    ):
        from memory.intelligence.extraction import ExtractedTask

        mocker.patch(
            "memory.services.conversation.extract_tasks",
            return_value=[ExtractedTask(title="Nova task", journey=None)],
        )
        conv = conversation_service.start_conversation(interface="cli", journey="test")
        for i in range(4):
            conversation_service.add_message(conv.id, role="user", content=f"Mensagem {i}")
        conversation_service.end_conversation(conv.id)
        tasks = store.find_tasks_by_title("Nova task", None)
        assert len(tasks) == 1

    def test_duplicate_task_not_created(
        self,
        conversation_service,
        task_service,
        store,
        mock_conversation_embedding,
        mock_extract_memories,
        mocker,
    ):
        from memory.intelligence.extraction import ExtractedTask

        # Criar task pré-existente
        task_service.add_task(title="Task existente")
        mocker.patch(
            "memory.services.conversation.extract_tasks",
            return_value=[ExtractedTask(title="Task existente", journey=None)],
        )
        conv = conversation_service.start_conversation(interface="cli", journey="test")
        for i in range(4):
            conversation_service.add_message(conv.id, role="user", content=f"Mensagem {i}")
        conversation_service.end_conversation(conv.id)
        tasks = store.find_tasks_by_title("Task existente", None)
        assert len(tasks) == 1  # não duplicou

    def test_task_extraction_failure_does_not_abort(
        self,
        conversation_service,
        store,
        mock_conversation_embedding,
        mock_extract_memories,
        mocker,
    ):
        mocker.patch(
            "memory.services.conversation.extract_tasks",
            side_effect=RuntimeError("LLM falhou"),
        )
        conv = conversation_service.start_conversation(interface="cli", journey="test")
        for i in range(4):
            conversation_service.add_message(conv.id, role="user", content=f"Mensagem {i}")
        # Não deve propagar a exceção
        result = conversation_service.end_conversation(conv.id)
        assert isinstance(result, list)

    # --- Smart extraction criteria ---

    def test_no_journey_skips_extraction(self, conversation_service, mocker):
        mock = mocker.patch("memory.services.conversation.extract_memories", return_value=[])
        conv = conversation_service.start_conversation(interface="cli")  # sem journey
        for i in range(6):
            conversation_service.add_message(conv.id, role="user", content=f"Mensagem {i}")
        result = conversation_service.end_conversation(conv.id, extract=True)
        assert result == []
        mock.assert_not_called()

    def test_too_few_messages_skips_extraction(self, conversation_service, mocker):
        mock = mocker.patch("memory.services.conversation.extract_memories", return_value=[])
        conv = conversation_service.start_conversation(interface="cli", journey="mirrormind")
        for i in range(3):  # apenas 3 mensagens — abaixo do mínimo
            conversation_service.add_message(conv.id, role="user", content=f"Mensagem {i}")
        result = conversation_service.end_conversation(conv.id, extract=True)
        assert result == []
        mock.assert_not_called()

    def test_journey_and_enough_messages_triggers_extraction(
        self,
        conversation_service,
        mock_conversation_embedding,
        mock_extract_tasks,
        mocker,
    ):
        from memory.models import ExtractedMemory

        mock = mocker.patch(
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
        conv = conversation_service.start_conversation(interface="cli", journey="mirrormind")
        for i in range(4):  # exatamente no limite mínimo
            conversation_service.add_message(conv.id, role="user", content=f"Mensagem {i}")
        result = conversation_service.end_conversation(conv.id, extract=True)
        assert len(result) == 1
        mock.assert_called_once()


class TestExtractionTracking:
    def test_end_conversation_marks_extracted_in_metadata(
        self,
        conversation_service,
        store,
        mock_conversation_embedding,
        mock_extract_memories,
        mock_extract_tasks,
    ):
        import json

        conv = conversation_service.start_conversation(interface="cli", journey="test")
        for i in range(4):
            conversation_service.add_message(conv.id, role="user", content=f"Msg {i}")
        conversation_service.end_conversation(conv.id, extract=True)
        stored = store.get_conversation(conv.id)
        assert stored.metadata is not None
        meta = json.loads(stored.metadata)
        assert meta.get("extracted") is True

    def test_no_metadata_set_when_criteria_unmet(self, conversation_service, store):
        conv = conversation_service.start_conversation(interface="cli", journey="test")
        for i in range(3):  # below minimum
            conversation_service.add_message(conv.id, role="user", content=f"Msg {i}")
        conversation_service.end_conversation(conv.id, extract=True)
        stored = store.get_conversation(conv.id)
        assert stored.metadata is None or '"extracted"' not in (stored.metadata or "")

    def test_extract_conversation_marks_extracted(
        self,
        conversation_service,
        store,
        mock_conversation_embedding,
        mock_extract_memories,
        mock_extract_tasks,
    ):
        import json

        conv = conversation_service.start_conversation(interface="cli", journey="test")
        for i in range(4):
            conversation_service.add_message(conv.id, role="user", content=f"Msg {i}")
        conversation_service.end_conversation(conv.id, extract=False)
        conversation_service.extract_conversation(conv.id)
        stored = store.get_conversation(conv.id)
        assert stored.metadata is not None
        meta = json.loads(stored.metadata)
        assert meta.get("extracted") is True

    def test_get_unextracted_returns_pending(
        self,
        conversation_service,
        store,
        mock_conversation_embedding,
        mock_extract_memories,
        mock_extract_tasks,
    ):
        # Extracted conv
        conv_done = conversation_service.start_conversation(interface="cli", journey="test")
        for i in range(4):
            conversation_service.add_message(conv_done.id, role="user", content=f"Msg {i}")
        conversation_service.end_conversation(conv_done.id, extract=True)

        # Unextracted conv
        conv_pending = conversation_service.start_conversation(interface="cli", journey="test")
        for i in range(4):
            conversation_service.add_message(conv_pending.id, role="user", content=f"Msg {i}")
        conversation_service.end_conversation(conv_pending.id, extract=False)

        pending = store.get_unextracted_conversations()
        ids = [c.id for c in pending]
        assert conv_pending.id in ids
        assert conv_done.id not in ids
