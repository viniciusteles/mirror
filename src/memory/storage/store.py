"""CRUD operations for conversations, messages, and memories."""

import sqlite3
from datetime import datetime, timezone

from memory.db import get_connection
from memory.models import (
    Attachment,
    Conversation,
    Identity,
    Memory,
    Message,
    RuntimeSession,
    Task,
)

_UNSET = object()


class Store:
    def __init__(self, conn: sqlite3.Connection | None = None):
        self.conn = conn or get_connection()

    # --- Conversations ---

    def create_conversation(self, conv: Conversation) -> Conversation:
        self.conn.execute(
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
        self.conn.commit()
        return conv

    def get_conversation(self, conv_id: str) -> Conversation | None:
        row = self.conn.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,)).fetchone()
        if not row:
            return None
        return Conversation(**dict(row))

    def get_conversations_in_range(self, start_time: str, end_time: str) -> list[Conversation]:
        """Return conversations whose interval overlaps the given range."""
        rows = self.conn.execute(
            """SELECT * FROM conversations
               WHERE started_at <= ? AND (ended_at >= ? OR ended_at IS NULL)""",
            (end_time, start_time),
        ).fetchall()
        return [Conversation(**dict(r)) for r in rows]

    def get_unextracted_conversations(self) -> list[Conversation]:
        """Return ended conversations eligible for extraction that haven't been extracted."""
        rows = self.conn.execute(
            """SELECT c.* FROM conversations c
               WHERE c.ended_at IS NOT NULL
                 AND c.journey IS NOT NULL
                 AND (c.metadata IS NULL OR json_extract(c.metadata, '$.extracted') IS NOT 1)
                 AND (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) >= 4"""
        ).fetchall()
        return [Conversation(**dict(r)) for r in rows]

    def get_open_conversations_idle_since(self, threshold_dt: str) -> list[Conversation]:
        """Return open conversations with no message activity since threshold_dt."""
        rows = self.conn.execute(
            """SELECT c.* FROM conversations c
               WHERE c.ended_at IS NULL
                 AND (
                   (SELECT MAX(m.created_at) FROM messages m WHERE m.conversation_id = c.id) < ?
                   OR NOT EXISTS (SELECT 1 FROM messages m WHERE m.conversation_id = c.id)
                 )""",
            (threshold_dt,),
        ).fetchall()
        return [Conversation(**dict(r)) for r in rows]

    def update_conversation(self, conv_id: str, **kwargs) -> None:
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        vals = [*list(kwargs.values()), conv_id]
        self.conn.execute(f"UPDATE conversations SET {sets} WHERE id = ?", vals)
        self.conn.commit()

    # --- Runtime Sessions ---

    def get_runtime_session(self, session_id: str) -> RuntimeSession | None:
        row = self.conn.execute(
            "SELECT * FROM runtime_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if not row:
            return None
        data = dict(row)
        data["mirror_active"] = bool(data["mirror_active"])
        data["hook_injected"] = bool(data["hook_injected"])
        data["active"] = bool(data["active"])
        return RuntimeSession(**data)

    def get_latest_runtime_defaults(
        self,
        *,
        exclude_session_id: str | None = None,
    ) -> tuple[str | None, str | None]:
        """Return the most recently used persona and journey across runtime sessions.

        Persona and journey are resolved independently so a recent session with only
        one of those fields does not erase the other sticky default.
        """
        persona_sql = """
            SELECT persona
            FROM runtime_sessions
            WHERE persona IS NOT NULL
        """
        journey_sql = """
            SELECT journey
            FROM runtime_sessions
            WHERE journey IS NOT NULL
        """
        params: list[str] = []
        if exclude_session_id:
            persona_sql += " AND session_id != ?"
            journey_sql += " AND session_id != ?"
            params.append(exclude_session_id)
        persona_sql += " ORDER BY updated_at DESC LIMIT 1"
        journey_sql += " ORDER BY updated_at DESC LIMIT 1"

        persona_row = self.conn.execute(persona_sql, params).fetchone()
        journey_row = self.conn.execute(journey_sql, params).fetchone()
        persona = persona_row["persona"] if persona_row else None
        journey = journey_row["journey"] if journey_row else None
        return persona, journey

    def upsert_runtime_session(
        self,
        session_id: str,
        *,
        conversation_id: str | None = None,
        interface: str | None = None,
        mirror_active: bool | None = None,
        persona: str | None = None,
        journey: str | None = None,
        hook_injected: bool | None = None,
        active: bool | None = None,
        closed_at: str | None | object = _UNSET,
        metadata: str | None | object = _UNSET,
    ) -> RuntimeSession:
        from memory.models import _now

        now = _now()
        existing = self.get_runtime_session(session_id)
        started_at = existing.started_at if existing else now
        resolved_closed_at = (
            closed_at if closed_at is not _UNSET else (existing.closed_at if existing else None)
        )
        resolved_metadata = (
            metadata if metadata is not _UNSET else (existing.metadata if existing else None)
        )
        record = RuntimeSession(
            session_id=session_id,
            conversation_id=conversation_id
            if conversation_id is not None
            else (existing.conversation_id if existing else None),
            interface=interface
            if interface is not None
            else (existing.interface if existing else None),
            mirror_active=(
                mirror_active
                if mirror_active is not None
                else (existing.mirror_active if existing else False)
            ),
            persona=persona if persona is not None else (existing.persona if existing else None),
            journey=journey if journey is not None else (existing.journey if existing else None),
            hook_injected=(
                hook_injected
                if hook_injected is not None
                else (existing.hook_injected if existing else False)
            ),
            active=active if active is not None else (existing.active if existing else True),
            started_at=started_at,
            updated_at=now,
            closed_at=resolved_closed_at if isinstance(resolved_closed_at, str) else None,
            metadata=resolved_metadata if isinstance(resolved_metadata, str) else None,
        )
        self.conn.execute(
            """INSERT INTO runtime_sessions
               (session_id, conversation_id, interface, mirror_active, persona, journey,
                hook_injected, active, started_at, updated_at, closed_at, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(session_id) DO UPDATE SET
                 conversation_id = excluded.conversation_id,
                 interface = excluded.interface,
                 mirror_active = excluded.mirror_active,
                 persona = excluded.persona,
                 journey = excluded.journey,
                 hook_injected = excluded.hook_injected,
                 active = excluded.active,
                 updated_at = excluded.updated_at,
                 closed_at = excluded.closed_at,
                 metadata = excluded.metadata""",
            (
                record.session_id,
                record.conversation_id,
                record.interface,
                int(record.mirror_active),
                record.persona,
                record.journey,
                int(record.hook_injected),
                int(record.active),
                record.started_at,
                record.updated_at,
                record.closed_at,
                record.metadata,
            ),
        )
        self.conn.commit()
        return record

    def get_or_create_runtime_session_conversation(
        self,
        session_id: str,
        *,
        interface: str,
        persona: str | None = None,
        journey: str | None = None,
        title: str | None = None,
    ) -> Conversation:
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            row = self.conn.execute(
                "SELECT conversation_id FROM runtime_sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if row and row["conversation_id"]:
                existing = self.conn.execute(
                    "SELECT * FROM conversations WHERE id = ?",
                    (row["conversation_id"],),
                ).fetchone()
                if existing:
                    self.conn.commit()
                    return Conversation(**dict(existing))

            conv = Conversation(interface=interface, persona=persona, journey=journey, title=title)
            self.conn.execute(
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
            self.conn.execute(
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
            self.conn.commit()
            return conv
        except Exception:
            self.conn.rollback()
            raise

    def get_active_runtime_conversation_ids(self) -> set[str]:
        rows = self.conn.execute(
            "SELECT conversation_id FROM runtime_sessions WHERE active = 1 AND conversation_id IS NOT NULL"
        ).fetchall()
        return {row["conversation_id"] for row in rows}

    def get_active_runtime_session_ids(self, interface: str) -> list[str]:
        """Return active runtime session ids for one interface, newest first."""
        rows = self.conn.execute(
            """SELECT session_id FROM runtime_sessions
               WHERE active = 1 AND interface = ?
               ORDER BY updated_at DESC""",
            (interface,),
        ).fetchall()
        return [row["session_id"] for row in rows]

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

    def get_recent_conversations_by_journey(
        self, journey: str, limit: int = 5
    ) -> list[Conversation]:
        rows = self.conn.execute(
            "SELECT * FROM conversations WHERE journey = ? ORDER BY started_at DESC LIMIT ?",
            (journey, limit),
        ).fetchall()
        return [Conversation(**dict(r)) for r in rows]

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

    # --- Identity ---

    def upsert_identity(self, identity: Identity) -> Identity:
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        existing = self.get_identity(identity.layer, identity.key)
        if existing:
            self.conn.execute(
                """UPDATE identity SET content = ?, version = ?, updated_at = ?, metadata = ?
                   WHERE layer = ? AND key = ?""",
                (
                    identity.content,
                    identity.version,
                    now,
                    identity.metadata,
                    identity.layer,
                    identity.key,
                ),
            )
            identity.id = existing.id
            identity.updated_at = now
        else:
            identity.created_at = now
            identity.updated_at = now
            self.conn.execute(
                """INSERT INTO identity (id, layer, key, content, version, created_at, updated_at, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    identity.id,
                    identity.layer,
                    identity.key,
                    identity.content,
                    identity.version,
                    identity.created_at,
                    identity.updated_at,
                    identity.metadata,
                ),
            )
        self.conn.commit()
        return identity

    def get_identity(self, layer: str, key: str) -> Identity | None:
        row = self.conn.execute(
            "SELECT * FROM identity WHERE layer = ? AND key = ?", (layer, key)
        ).fetchone()
        if not row:
            return None
        return Identity(**dict(row))

    def get_identity_by_layer(self, layer: str) -> list[Identity]:
        rows = self.conn.execute(
            "SELECT * FROM identity WHERE layer = ? ORDER BY key", (layer,)
        ).fetchall()
        return [Identity(**dict(r)) for r in rows]

    def get_all_identity(self) -> list[Identity]:
        rows = self.conn.execute("SELECT * FROM identity ORDER BY layer, key").fetchall()
        return [Identity(**dict(r)) for r in rows]

    def update_identity_metadata(self, layer: str, key: str, metadata: str) -> None:
        from memory.models import _now

        self.conn.execute(
            "UPDATE identity SET metadata = ?, updated_at = ? WHERE layer = ? AND key = ?",
            (metadata, _now(), layer, key),
        )
        self.conn.commit()

    def delete_identity(self, layer: str, key: str) -> bool:
        cursor = self.conn.execute("DELETE FROM identity WHERE layer = ? AND key = ?", (layer, key))
        self.conn.commit()
        return cursor.rowcount > 0

    # --- Attachments ---

    def create_attachment(self, att: Attachment) -> Attachment:
        self.conn.execute(
            """INSERT INTO attachments
               (id, journey_id, name, description, content, content_type,
                tags, embedding, created_at, updated_at, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                att.id,
                att.journey_id,
                att.name,
                att.description,
                att.content,
                att.content_type,
                att.tags,
                att.embedding,
                att.created_at,
                att.updated_at,
                att.metadata,
            ),
        )
        self.conn.commit()
        return att

    def get_attachment(self, attachment_id: str) -> Attachment | None:
        row = self.conn.execute(
            "SELECT * FROM attachments WHERE id = ?", (attachment_id,)
        ).fetchone()
        if not row:
            return None
        return Attachment(**dict(row))

    def get_attachment_by_name(self, journey_id: str, name: str) -> Attachment | None:
        row = self.conn.execute(
            "SELECT * FROM attachments WHERE journey_id = ? AND name = ?",
            (journey_id, name),
        ).fetchone()
        if not row:
            return None
        return Attachment(**dict(row))

    def get_attachments_by_journey(self, journey_id: str) -> list[Attachment]:
        rows = self.conn.execute(
            "SELECT * FROM attachments WHERE journey_id = ? ORDER BY created_at",
            (journey_id,),
        ).fetchall()
        return [Attachment(**dict(r)) for r in rows]

    def update_attachment(self, attachment_id: str, **kwargs) -> None:
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        vals = [*list(kwargs.values()), attachment_id]
        self.conn.execute(f"UPDATE attachments SET {sets} WHERE id = ?", vals)
        self.conn.commit()

    def delete_attachment(self, attachment_id: str) -> bool:
        cursor = self.conn.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # --- Tasks ---

    def create_task(self, task: Task) -> Task:
        self.conn.execute(
            """INSERT INTO tasks
               (id, journey, title, status, due_date, scheduled_at, time_hint,
                stage, context, source, created_at, updated_at, completed_at, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                task.id,
                task.journey,
                task.title,
                task.status,
                task.due_date,
                task.scheduled_at,
                task.time_hint,
                task.stage,
                task.context,
                task.source,
                task.created_at,
                task.updated_at,
                task.completed_at,
                task.metadata,
            ),
        )
        self.conn.commit()
        return task

    def get_tasks_for_week(self, start_date: str, end_date: str) -> list[Task]:
        """Return week tasks/appointments by due_date or scheduled_at."""
        rows = self.conn.execute(
            """SELECT * FROM tasks
               WHERE (due_date >= ? AND due_date <= ?)
                  OR (scheduled_at >= ? AND scheduled_at <= ?)
               ORDER BY due_date ASC NULLS LAST, scheduled_at ASC NULLS LAST""",
            (start_date, end_date, start_date, end_date + "T23:59"),
        ).fetchall()
        return [Task(**dict(r)) for r in rows]

    def get_task(self, task_id: str) -> Task | None:
        row = self.conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not row:
            return None
        return Task(**dict(row))

    def update_task(self, task_id: str, **kwargs) -> None:
        from memory.models import _now

        kwargs["updated_at"] = _now()
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        vals = [*list(kwargs.values()), task_id]
        self.conn.execute(f"UPDATE tasks SET {sets} WHERE id = ?", vals)
        self.conn.commit()

    def delete_task(self, task_id: str) -> bool:
        cursor = self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_tasks_by_journey(self, journey: str) -> list[Task]:
        rows = self.conn.execute(
            "SELECT * FROM tasks WHERE journey = ? ORDER BY due_date ASC NULLS LAST, created_at ASC",
            (journey,),
        ).fetchall()
        return [Task(**dict(r)) for r in rows]

    def get_tasks_by_status(self, status: str) -> list[Task]:
        rows = self.conn.execute(
            "SELECT * FROM tasks WHERE status = ? ORDER BY due_date ASC NULLS LAST, created_at ASC",
            (status,),
        ).fetchall()
        return [Task(**dict(r)) for r in rows]

    def get_open_tasks(self, journey: str | None = None) -> list[Task]:
        if journey:
            rows = self.conn.execute(
                """SELECT * FROM tasks WHERE status IN ('todo', 'doing', 'blocked')
                   AND journey = ?
                   ORDER BY due_date ASC NULLS LAST, created_at ASC""",
                (journey,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """SELECT * FROM tasks WHERE status IN ('todo', 'doing', 'blocked')
                   ORDER BY due_date ASC NULLS LAST, created_at ASC"""
            ).fetchall()
        return [Task(**dict(r)) for r in rows]

    def get_all_tasks(self) -> list[Task]:
        rows = self.conn.execute(
            "SELECT * FROM tasks ORDER BY status, due_date ASC NULLS LAST, created_at ASC"
        ).fetchall()
        return [Task(**dict(r)) for r in rows]

    def find_tasks_by_title(self, title_fragment: str, journey: str | None = None) -> list[Task]:
        if journey:
            rows = self.conn.execute(
                "SELECT * FROM tasks WHERE title LIKE ? AND journey = ? ORDER BY created_at DESC",
                (f"%{title_fragment}%", journey),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM tasks WHERE title LIKE ? ORDER BY created_at DESC",
                (f"%{title_fragment}%",),
            ).fetchall()
        return [Task(**dict(r)) for r in rows]

    def get_all_attachments_with_embeddings(self, journey_id: str) -> list[Attachment]:
        rows = self.conn.execute(
            "SELECT * FROM attachments WHERE journey_id = ? AND embedding IS NOT NULL ORDER BY created_at",
            (journey_id,),
        ).fetchall()
        return [Attachment(**dict(r)) for r in rows]

    def get_all_attachments_with_embeddings_global(self) -> list[Attachment]:
        """Return all attachments with embeddings across all journeys."""
        rows = self.conn.execute(
            "SELECT * FROM attachments WHERE embedding IS NOT NULL ORDER BY created_at",
        ).fetchall()
        return [Attachment(**dict(r)) for r in rows]
