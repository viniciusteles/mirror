"""Memory persistence operations."""

from datetime import datetime, timezone

from memory.models import Memory
from memory.storage.base import ConnectionBacked


class MemoryStore(ConnectionBacked):
    # --- Memories ---

    def create_memory(self, mem: Memory) -> Memory:
        self.conn.execute(
            """INSERT INTO memories
               (id, conversation_id, memory_type, layer, title, content, context,
                journey, persona, tags, created_at, relevance_score, embedding, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                mem.id,
                mem.conversation_id,
                mem.memory_type,
                mem.layer,
                mem.title,
                mem.content,
                mem.context,
                mem.journey,
                mem.persona,
                mem.tags,
                mem.created_at,
                mem.relevance_score,
                mem.embedding,
                mem.metadata,
            ),
        )
        self.conn.commit()
        return mem

    def get_memory(self, memory_id: str) -> Memory | None:
        row = self.conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,)).fetchone()
        if not row:
            return None
        return Memory(**dict(row))

    def get_memories_by_type(self, memory_type: str) -> list[Memory]:
        rows = self.conn.execute(
            "SELECT * FROM memories WHERE memory_type = ? ORDER BY created_at DESC",
            (memory_type,),
        ).fetchall()
        return [Memory(**dict(r)) for r in rows]

    def get_memories_by_layer(self, layer: str) -> list[Memory]:
        rows = self.conn.execute(
            "SELECT * FROM memories WHERE layer = ? ORDER BY created_at DESC",
            (layer,),
        ).fetchall()
        return [Memory(**dict(r)) for r in rows]

    def get_memories_by_journey(self, journey: str) -> list[Memory]:
        rows = self.conn.execute(
            "SELECT * FROM memories WHERE journey = ? ORDER BY created_at DESC",
            (journey,),
        ).fetchall()
        return [Memory(**dict(r)) for r in rows]

    def get_all_memories_with_embeddings(self) -> list[Memory]:
        rows = self.conn.execute(
            "SELECT * FROM memories WHERE embedding IS NOT NULL ORDER BY created_at DESC"
        ).fetchall()
        return [Memory(**dict(r)) for r in rows]

    def get_memories_timeline(self, start: str, end: str) -> list[Memory]:
        rows = self.conn.execute(
            "SELECT * FROM memories WHERE created_at >= ? AND created_at <= ? ORDER BY created_at",
            (start, end),
        ).fetchall()
        return [Memory(**dict(r)) for r in rows]

    # --- Access Log ---

    def log_access(self, memory_id: str, context: str | None = None) -> None:
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.conn.execute(
            "INSERT INTO memory_access_log (memory_id, accessed_at, access_context) VALUES (?, ?, ?)",
            (memory_id, now, context),
        )
        self.conn.commit()

    def get_access_count(self, memory_id: str) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) as cnt FROM memory_access_log WHERE memory_id = ?",
            (memory_id,),
        ).fetchone()
        return row["cnt"] if row else 0

    # --- Conversation Embeddings ---

    def store_conversation_embedding(self, conversation_id: str, embedding: bytes) -> None:
        self.conn.execute(
            """INSERT OR REPLACE INTO conversation_embeddings
               (conversation_id, summary_embedding) VALUES (?, ?)""",
            (conversation_id, embedding),
        )
        self.conn.commit()
