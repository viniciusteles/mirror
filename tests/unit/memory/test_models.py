"""Testes unitários para memory.models."""

import string

import pytest
from pydantic import ValidationError

from memory.models import (
    Attachment,
    Conversation,
    ExtractedMemory,
    ExtractedWeekItem,
    Identity,
    Memory,
    Message,
    Task,
    _now,
    _uuid,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fixed_uuid(mocker):
    mocker.patch("memory.models._uuid", return_value="deadbeef")


@pytest.fixture
def fixed_now(mocker):
    mocker.patch("memory.models._now", return_value="2026-04-12T00:00:00Z")


# ---------------------------------------------------------------------------
# _uuid / _now helpers
# ---------------------------------------------------------------------------


class TestUuidHelper:
    def test_returns_8_char_string(self):
        result = _uuid()
        assert len(result) == 8

    def test_returns_hex_digits_only(self):
        result = _uuid()
        assert all(c in string.hexdigits for c in result)

    def test_uniqueness(self):
        results = {_uuid() for _ in range(100)}
        assert len(results) == 100


class TestNowHelper:
    def test_ends_with_z(self):
        result = _now()
        assert result.endswith("Z")

    def test_parseable_iso_datetime(self):
        from datetime import datetime

        result = _now()
        datetime.fromisoformat(result.rstrip("Z"))


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------


class TestMessageModel:
    def test_default_id_generated(self):
        msg = Message(conversation_id="c1", role="user", content="hi")
        assert len(msg.id) == 8
        assert all(c in string.hexdigits for c in msg.id)

    def test_explicit_id_preserved(self):
        msg = Message(id="abcd1234", conversation_id="c1", role="user", content="hi")
        assert msg.id == "abcd1234"

    def test_created_at_is_iso_z(self):
        from datetime import datetime

        msg = Message(conversation_id="c1", role="user", content="hi")
        assert msg.created_at.endswith("Z")
        datetime.fromisoformat(msg.created_at.rstrip("Z"))

    def test_required_fields_enforced(self):
        with pytest.raises(ValidationError):
            Message()

    def test_optional_token_count_defaults_none(self):
        msg = Message(conversation_id="c1", role="user", content="hi")
        assert msg.token_count is None

    def test_optional_metadata_defaults_none(self):
        msg = Message(conversation_id="c1", role="user", content="hi")
        assert msg.metadata is None

    def test_fixed_id_used(self, fixed_uuid):
        msg = Message(conversation_id="c1", role="user", content="hi")
        assert msg.id == "deadbeef"

    def test_fixed_now_used(self, fixed_now):
        msg = Message(conversation_id="c1", role="user", content="hi")
        assert msg.created_at == "2026-04-12T00:00:00Z"


# ---------------------------------------------------------------------------
# Conversation
# ---------------------------------------------------------------------------


class TestConversationModel:
    def test_optional_fields_default_none(self):
        conv = Conversation(interface="claude_code")
        for field in ("title", "ended_at", "persona", "journey", "summary", "tags", "metadata"):
            assert getattr(conv, field) is None

    def test_required_interface_enforced(self):
        with pytest.raises(ValidationError):
            Conversation()

    def test_started_at_generated(self):
        conv = Conversation(interface="cli")
        assert conv.started_at and conv.started_at.endswith("Z")

    def test_id_generated(self):
        conv = Conversation(interface="cli")
        assert len(conv.id) == 8

    def test_journey_field_round_trips(self):
        conv = Conversation(interface="cli", journey="mirror-poc")
        assert conv.journey == "mirror-poc"

    def test_old_journey_alias_rejected(self):
        with pytest.raises(ValidationError):
            Conversation(interface="cli", travessia="mirror-poc")


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------


class TestMemoryModel:
    def test_layer_defaults_to_ego(self):
        mem = Memory(memory_type="insight", title="T", content="C")
        assert mem.layer == "ego"

    def test_relevance_score_defaults_to_1(self):
        mem = Memory(memory_type="insight", title="T", content="C")
        assert mem.relevance_score == 1.0

    def test_required_fields_enforced(self):
        with pytest.raises(ValidationError):
            Memory()

    def test_embedding_defaults_none(self):
        mem = Memory(memory_type="insight", title="T", content="C")
        assert mem.embedding is None

    def test_optional_fields_default_none(self):
        mem = Memory(memory_type="insight", title="T", content="C")
        for field in ("conversation_id", "context", "journey", "persona", "tags", "metadata"):
            assert getattr(mem, field) is None

    def test_journey_field_round_trips(self):
        mem = Memory(memory_type="insight", title="T", content="C", journey="mirror-poc")
        assert mem.journey == "mirror-poc"

    def test_old_journey_alias_rejected(self):
        with pytest.raises(ValidationError):
            Memory(memory_type="insight", title="T", content="C", travessia="mirror-poc")


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


class TestIdentityModel:
    def test_version_defaults_to_1_0_0(self):
        identity = Identity(layer="ego", key="identity", content="...")
        assert identity.version == "1.0.0"

    def test_updated_at_generated(self):
        identity = Identity(layer="ego", key="identity", content="...")
        assert identity.updated_at and identity.updated_at.endswith("Z")

    def test_required_fields_enforced(self):
        with pytest.raises(ValidationError):
            Identity()

    def test_metadata_defaults_none(self):
        identity = Identity(layer="ego", key="identity", content="...")
        assert identity.metadata is None


# ---------------------------------------------------------------------------
# Attachment
# ---------------------------------------------------------------------------


class TestAttachmentModel:
    def test_content_type_defaults_to_markdown(self):
        att = Attachment(journey_id="t1", name="doc", content="...")
        assert att.content_type == "markdown"

    def test_required_journey_id(self):
        with pytest.raises(ValidationError):
            Attachment(name="doc", content="...")

    def test_optional_description_defaults_none(self):
        att = Attachment(journey_id="t1", name="doc", content="...")
        assert att.description is None

    def test_journey_id_field_round_trips(self):
        att = Attachment(journey_id="t1", name="doc", content="...")
        assert att.journey_id == "t1"

    def test_old_journey_id_alias_rejected(self):
        with pytest.raises(ValidationError):
            Attachment(travessia_id="t1", name="doc", content="...")


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------


class TestTaskModel:
    def test_status_defaults_to_todo(self):
        task = Task(title="Fazer algo")
        assert task.status == "todo"

    def test_source_defaults_to_manual(self):
        task = Task(title="Fazer algo")
        assert task.source == "manual"

    def test_completed_at_defaults_none(self):
        task = Task(title="Fazer algo")
        assert task.completed_at is None

    def test_required_title_enforced(self):
        with pytest.raises(ValidationError):
            Task()

    def test_optional_fields_default_none(self):
        task = Task(title="Fazer algo")
        for field in ("journey", "due_date", "scheduled_at", "time_hint", "stage", "context"):
            assert getattr(task, field) is None

    def test_journey_field_round_trips(self):
        task = Task(title="Fazer algo", journey="mirror-poc")
        assert task.journey == "mirror-poc"

    def test_old_journey_alias_rejected(self):
        with pytest.raises(ValidationError):
            Task(title="Fazer algo", travessia="mirror-poc")


# ---------------------------------------------------------------------------
# ExtractedWeekItem
# ---------------------------------------------------------------------------


class TestExtractedWeekItemModel:
    def test_due_date_required(self):
        with pytest.raises(ValidationError):
            ExtractedWeekItem(title="Reunião")

    def test_scheduled_at_defaults_none(self):
        item = ExtractedWeekItem(title="Reunião", due_date="2026-04-14")
        assert item.scheduled_at is None

    def test_time_hint_defaults_none(self):
        item = ExtractedWeekItem(title="Reunião", due_date="2026-04-14")
        assert item.time_hint is None

    def test_optional_journey_defaults_none(self):
        item = ExtractedWeekItem(title="Reunião", due_date="2026-04-14")
        assert item.journey is None


# ---------------------------------------------------------------------------
# ExtractedMemory
# ---------------------------------------------------------------------------


class TestExtractedMemoryModel:
    def test_layer_defaults_to_ego(self):
        em = ExtractedMemory(title="T", content="C", memory_type="insight")
        assert em.layer == "ego"

    def test_tags_defaults_to_empty_list(self):
        em = ExtractedMemory(title="T", content="C", memory_type="insight")
        assert em.tags == []

    def test_required_fields_enforced(self):
        with pytest.raises(ValidationError):
            ExtractedMemory()

    def test_optional_persona_defaults_none(self):
        em = ExtractedMemory(title="T", content="C", memory_type="insight")
        assert em.persona is None

    def test_optional_journey_defaults_none(self):
        em = ExtractedMemory(title="T", content="C", memory_type="insight")
        assert em.journey is None
