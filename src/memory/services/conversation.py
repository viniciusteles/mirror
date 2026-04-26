"""ConversationService: conversation lifecycle and automatic extraction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from memory.intelligence.embeddings import embedding_to_bytes, generate_embedding
from memory.intelligence.extraction import extract_memories, extract_tasks
from memory.models import Conversation, ConversationSummary, Memory, Message
from memory.storage.store import Store

if TYPE_CHECKING:
    from memory.services.memory import MemoryService
    from memory.services.tasks import TaskService


class ConversationService:
    def __init__(
        self,
        store: Store,
        memories: MemoryService,
        tasks: TaskService | None = None,
    ) -> None:
        self.store = store
        self.memories = memories
        if tasks is None:
            raise TypeError("ConversationService requires tasks")
        self.tasks: TaskService = tasks

    def start_conversation(
        self,
        interface: str,
        persona: str | None = None,
        journey: str | None = None,
        title: str | None = None,
    ) -> Conversation:
        """Start a new conversation."""
        conv = Conversation(
            interface=interface,
            persona=persona,
            journey=journey,
            title=title,
        )
        return self.store.create_conversation(conv)

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        token_count: int | None = None,
    ) -> Message:
        """Add a message to an existing conversation."""
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            token_count=token_count,
        )
        return self.store.add_message(msg)

    def find_by_id_prefix(self, prefix: str) -> Conversation | None:
        """Return the latest conversation whose id starts with prefix."""
        row = self.store.conn.execute(
            "SELECT * FROM conversations WHERE id LIKE ? ORDER BY started_at DESC LIMIT 1",
            (f"{prefix}%",),
        ).fetchone()
        if not row:
            return None
        return Conversation(**dict(row))

    def list_recent(
        self,
        *,
        limit: int = 20,
        journey: str | None = None,
        persona: str | None = None,
    ) -> list[ConversationSummary]:
        """Return recent conversation summaries with optional filters."""
        conditions = ["1=1"]
        params: list[str | int] = []

        if journey:
            conditions.append("journey = ?")
            params.append(journey)
        if persona:
            conditions.append("persona = ?")
            params.append(persona)

        where = " AND ".join(conditions)
        params.append(limit)

        rows = self.store.conn.execute(
            f"""SELECT id, title, started_at, persona, journey,
                       (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count
                FROM conversations c
                WHERE {where}
                ORDER BY started_at DESC
                LIMIT ?""",
            params,
        ).fetchall()
        return [ConversationSummary(**dict(row)) for row in rows]

    def end_conversation(
        self,
        conversation_id: str,
        extract: bool = True,
    ) -> list[Memory]:
        """End a conversation, extract memories/tasks, generate embeddings, and store them."""
        from memory.models import _now

        self.store.update_conversation(conversation_id, ended_at=_now())

        if not extract:
            return []

        return self._run_extraction(conversation_id)

    def extract_conversation(self, conversation_id: str) -> list[Memory]:
        """Extract memories from an already-ended conversation."""
        return self._run_extraction(conversation_id)

    def _run_extraction(self, conversation_id: str) -> list[Memory]:
        """Run memory/task extraction. Marks metadata.extracted=True on success."""
        import json

        conv = self.store.get_conversation(conversation_id)
        messages = self.store.get_messages(conversation_id)

        # Extraction requires a journey and at least 4 messages.
        if not messages or not conv or not conv.journey or len(messages) < 4:
            return []

        # Load the user's first name for the transcript when available.
        user_name = "User"
        try:
            import re

            user_identity = self.store.get_identity("user", "identity")
            if user_identity and user_identity.content:
                match = re.search(
                    r"(?:You are talking to|Você está falando com) ([A-Z][a-zA-Záéíóúãõ]+)",
                    user_identity.content,
                )
                if match:
                    user_name = match.group(1)
        except Exception:
            pass

        # Extract memories through the LLM.
        extracted = extract_memories(
            messages,
            persona=conv.persona if conv else None,
            journey=conv.journey if conv else None,
            user_name=user_name,
        )

        # Extract tasks through the LLM.
        try:
            extracted_tasks = extract_tasks(
                messages,
                journey=conv.journey if conv else None,
                user_name=user_name,
            )
            for et in extracted_tasks:
                existing = self.store.find_tasks_by_title(et.title, et.journey)
                if not existing:
                    self.tasks.add_task(
                        title=et.title,
                        journey=et.journey,
                        due_date=et.due_date,
                        stage=et.stage,
                        context=et.context,
                        source="conversation",
                    )
        except Exception:
            pass  # Task extraction failure should not block memory extraction.

        # Generate a conversation summary for embedding.
        summary_parts = []
        for msg in messages:
            if msg.role in ("user", "assistant"):
                summary_parts.append(msg.content[:500])
        summary_text = " ".join(summary_parts)[:2000]

        if summary_text:
            summary_emb = generate_embedding(summary_text)
            self.store.store_conversation_embedding(
                conversation_id, embedding_to_bytes(summary_emb)
            )
            self.store.update_conversation(conversation_id, summary=summary_text[:500])

        # Persist extracted memories with embeddings.
        stored_memories = []
        for ext in extracted:
            stored = self.memories.add_memory(
                title=ext.title,
                content=ext.content,
                memory_type=ext.memory_type,
                layer=ext.layer,
                context=ext.context,
                journey=ext.journey,
                persona=ext.persona,
                tags=ext.tags,
                conversation_id=conversation_id,
            )
            stored_memories.append(stored)

        # Mark as extracted so extract_pending skips this conversation.
        meta = json.loads(conv.metadata or "{}")
        meta["extracted"] = True
        self.store.update_conversation(conversation_id, metadata=json.dumps(meta))

        return stored_memories
