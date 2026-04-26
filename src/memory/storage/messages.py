"""Message persistence operations."""

from memory.models import Message
from memory.storage.base import ConnectionBacked


class MessageStore(ConnectionBacked):
    # --- Messages ---

    def add_message(self, msg: Message) -> Message:
        self.conn.execute(
            """INSERT INTO messages
               (id, conversation_id, role, content, created_at, token_count, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                msg.id,
                msg.conversation_id,
                msg.role,
                msg.content,
                msg.created_at,
                msg.token_count,
                msg.metadata,
            ),
        )
        self.conn.commit()
        return msg

    def get_messages(self, conversation_id: str) -> list[Message]:
        rows = self.conn.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at",
            (conversation_id,),
        ).fetchall()
        return [Message(**dict(r)) for r in rows]
