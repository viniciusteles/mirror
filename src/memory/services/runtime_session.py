"""Runtime session workflow service."""

from memory.models import Conversation
from memory.storage.store import Store


class RuntimeSessionService:
    def __init__(self, store: Store):
        self.store = store

    def get_or_create_conversation(
        self,
        session_id: str,
        *,
        interface: str,
        persona: str | None = None,
        journey: str | None = None,
        title: str | None = None,
    ) -> Conversation:
        """Return the bound conversation for a runtime session, creating it if needed."""
        self.store.conn.execute("BEGIN IMMEDIATE")
        try:
            row = self.store.conn.execute(
                "SELECT conversation_id FROM runtime_sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if row and row["conversation_id"]:
                existing = self.store.conn.execute(
                    "SELECT * FROM conversations WHERE id = ?",
                    (row["conversation_id"],),
                ).fetchone()
                if existing:
                    self.store.conn.commit()
                    return Conversation(**dict(existing))

            conv = Conversation(interface=interface, persona=persona, journey=journey, title=title)
            self.store.conn.execute(
                """INSERT INTO conversations
                   (id, title, started_at, ended_at, interface, persona, journey, summary, tags, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    conv.id,
                    conv.title,
                    conv.started_at,
                    conv.ended_at,
                    conv.interface,
                    conv.persona,
                    conv.journey,
                    conv.summary,
                    conv.tags,
                    conv.metadata,
                ),
            )
            self.store.conn.execute(
                """INSERT INTO runtime_sessions
                   (session_id, conversation_id, interface, mirror_active, persona, journey,
                    hook_injected, active, started_at, updated_at, closed_at, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(session_id) DO UPDATE SET
                     conversation_id = excluded.conversation_id,
                     interface = excluded.interface,
                     persona = excluded.persona,
                     journey = excluded.journey,
                     active = 1,
                     closed_at = NULL,
                     updated_at = excluded.updated_at""",
                (
                    session_id,
                    conv.id,
                    interface,
                    0,
                    persona,
                    journey,
                    0,
                    1,
                    conv.started_at,
                    conv.started_at,
                    None,
                    None,
                ),
            )
            self.store.conn.commit()
            return conv
        except Exception:
            self.store.conn.rollback()
            raise
