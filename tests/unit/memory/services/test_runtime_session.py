"""Runtime session service behavior."""

from memory.models import Conversation, _now
from memory.services.runtime_session import RuntimeSessionService
from memory.storage.store import Store


def test_get_or_create_conversation_creates_conversation_and_runtime_session(db_conn):
    store = Store(db_conn)
    service = RuntimeSessionService(store)

    conversation = service.get_or_create_conversation(
        "sess-1",
        interface="pi",
        persona="engineer",
        journey="mirror",
        title="Initial title",
    )

    stored_conversation = store.get_conversation(conversation.id)
    runtime_session = store.get_runtime_session("sess-1")

    assert stored_conversation is not None
    assert stored_conversation.id == conversation.id
    assert stored_conversation.interface == "pi"
    assert stored_conversation.persona == "engineer"
    assert stored_conversation.journey == "mirror"
    assert stored_conversation.title == "Initial title"

    assert runtime_session is not None
    assert runtime_session.conversation_id == conversation.id
    assert runtime_session.interface == "pi"
    assert runtime_session.persona == "engineer"
    assert runtime_session.journey == "mirror"
    assert runtime_session.active is True


def test_get_or_create_conversation_returns_existing_conversation(db_conn):
    store = Store(db_conn)
    service = RuntimeSessionService(store)
    existing = store.create_conversation(Conversation(interface="pi", journey="mirror"))
    store.upsert_runtime_session(
        "sess-1",
        conversation_id=existing.id,
        interface="pi",
        journey="mirror",
    )

    conversation = service.get_or_create_conversation(
        "sess-1",
        interface="pi",
        persona="engineer",
        journey="mirror",
    )

    assert conversation.id == existing.id
    count = db_conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
    assert count == 1


def test_get_or_create_conversation_replaces_stale_conversation_binding(db_conn):
    store = Store(db_conn)
    service = RuntimeSessionService(store)
    db_conn.execute("PRAGMA foreign_keys=OFF")
    now = _now()
    db_conn.execute(
        """INSERT INTO runtime_sessions
           (session_id, conversation_id, interface, mirror_active, persona, journey,
            hook_injected, active, started_at, updated_at, closed_at, metadata)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "sess-1",
            "missing-conversation",
            "pi",
            0,
            "writer",
            "old-journey",
            0,
            1,
            now,
            now,
            None,
            None,
        ),
    )
    db_conn.commit()
    db_conn.execute("PRAGMA foreign_keys=ON")

    conversation = service.get_or_create_conversation(
        "sess-1",
        interface="claude_code",
        persona="engineer",
        journey="mirror",
    )
    runtime_session = store.get_runtime_session("sess-1")

    assert conversation.id != "missing-conversation"
    assert conversation.interface == "claude_code"
    assert conversation.persona == "engineer"
    assert conversation.journey == "mirror"
    assert runtime_session is not None
    assert runtime_session.conversation_id == conversation.id
    assert runtime_session.interface == "claude_code"
    assert runtime_session.persona == "engineer"
    assert runtime_session.journey == "mirror"
    assert runtime_session.active is True
    assert runtime_session.closed_at is None
