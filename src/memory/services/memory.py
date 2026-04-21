"""MemoryService: storage and search for memories and journal entries."""

import json

from memory.intelligence.embeddings import embedding_to_bytes, generate_embedding
from memory.intelligence.search import MemorySearch
from memory.models import Memory, SearchResult
from memory.storage.store import Store


class MemoryService:
    def __init__(self, store: Store, search_engine: MemorySearch) -> None:
        self.store = store
        self.search_engine = search_engine

    def add_memory(
        self,
        title: str,
        content: str,
        memory_type: str,
        layer: str = "ego",
        context: str | None = None,
        journey: str | None = None,
        persona: str | None = None,
        tags: list[str] | None = None,
        conversation_id: str | None = None,
    ) -> Memory:
        """Add a manual memory without automatic extraction."""
        embed_text = f"{title}. {content}"
        if context:
            embed_text += f" Context: {context}"

        emb = generate_embedding(embed_text)

        mem = Memory(
            conversation_id=conversation_id,
            memory_type=memory_type,
            layer=layer,
            title=title,
            content=content,
            context=context,
            journey=journey,
            persona=persona,
            tags=json.dumps(tags) if tags else None,
            embedding=embedding_to_bytes(emb),
        )
        return self.store.create_memory(mem)

    def search(
        self,
        query: str,
        limit: int = 5,
        memory_type: str | None = None,
        layer: str | None = None,
        journey: str | None = None,
    ) -> list[SearchResult]:
        """Search memories by hybrid similarity."""
        return self.search_engine.search(
            query,
            limit=limit,
            memory_type=memory_type,
            layer=layer,
            journey=journey,
        )

    def get_by_type(self, memory_type: str) -> list[Memory]:
        """Return all memories of one type."""
        return self.store.get_memories_by_type(memory_type)

    def get_by_layer(self, layer: str) -> list[Memory]:
        """Return all memories for one layer."""
        return self.store.get_memories_by_layer(layer)

    def get_by_journey(self, journey: str) -> list[Memory]:
        """Return all memories for one journey."""
        return self.store.get_memories_by_journey(journey)

    def get_timeline(self, start: str, end: str) -> list[Memory]:
        """Return memories in a time range."""
        return self.store.get_memories_timeline(start, end)

    def add_journal(
        self,
        content: str,
        title: str | None = None,
        layer: str | None = None,
        tags: list[str] | None = None,
        conversation_id: str | None = None,
        journey: str | None = None,
    ) -> Memory:
        """Add a journal entry, classifying it with an LLM when needed."""
        from memory.intelligence.extraction import classify_journal_entry

        if not title or not layer or not tags:
            classification = classify_journal_entry(content)
            title = title or classification["title"]
            layer = layer or classification["layer"]
            tags = tags or classification["tags"]

        return self.add_memory(
            title=title,
            content=content,
            memory_type="journal",
            layer=layer,
            tags=tags,
            conversation_id=conversation_id,
            journey=journey,
        )
