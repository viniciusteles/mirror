"""Pydantic models for the memory system."""

from datetime import datetime, timezone
from typing import NamedTuple

from pydantic import BaseModel, ConfigDict, Field


class _DomainModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class Message(BaseModel):
    id: str = Field(default_factory=lambda: _uuid())
    conversation_id: str
    role: str  # 'user', 'assistant', 'system'
    content: str
    created_at: str = Field(default_factory=lambda: _now())
    token_count: int | None = None
    metadata: str | None = None


class Conversation(_DomainModel):
    id: str = Field(default_factory=lambda: _uuid())
    title: str | None = None
    started_at: str = Field(default_factory=lambda: _now())
    ended_at: str | None = None
    interface: str  # 'claude_code', 'cli', 'django'
    persona: str | None = None
    journey: str | None = None
    summary: str | None = None
    tags: str | None = None  # JSON array
    metadata: str | None = None


class ConversationSummary(_DomainModel):
    id: str
    title: str | None = None
    started_at: str | None = None
    persona: str | None = None
    journey: str | None = None
    message_count: int = 0


class RuntimeSession(_DomainModel):
    session_id: str
    conversation_id: str | None = None
    interface: str | None = None
    mirror_active: bool = False
    persona: str | None = None
    journey: str | None = None
    hook_injected: bool = False
    active: bool = True
    started_at: str = Field(default_factory=lambda: _now())
    updated_at: str = Field(default_factory=lambda: _now())
    closed_at: str | None = None
    metadata: str | None = None


class MemorySummary(_DomainModel):
    id: str
    memory_type: str
    layer: str
    title: str
    content: str
    context: str | None = None
    journey: str | None = None
    persona: str | None = None
    tags: str | None = None
    created_at: str


class Memory(_DomainModel):
    id: str = Field(default_factory=lambda: _uuid())
    conversation_id: str | None = None
    memory_type: str  # 'decision', 'insight', 'idea', 'journal', 'tension', 'learning', 'pattern', 'commitment', 'reflection'
    layer: str = "ego"  # 'self', 'ego', 'shadow'
    title: str
    content: str
    context: str | None = None
    journey: str | None = None
    persona: str | None = None
    tags: str | None = None  # JSON array
    created_at: str = Field(default_factory=lambda: _now())
    relevance_score: float = 1.0
    embedding: bytes | None = None
    metadata: str | None = None


class Identity(BaseModel):
    id: str = Field(default_factory=lambda: _uuid())
    layer: str  # 'self', 'ego', 'user', 'organization', 'persona'
    key: str  # 'soul', 'behavior', 'identity', 'principles', or persona_id
    content: str
    version: str = "1.0.0"
    created_at: str = Field(default_factory=lambda: _now())
    updated_at: str = Field(default_factory=lambda: _now())
    metadata: str | None = None


class Attachment(_DomainModel):
    id: str = Field(default_factory=lambda: _uuid())
    journey_id: str
    name: str
    description: str | None = None
    content: str
    content_type: str = "markdown"  # markdown, text, yaml
    tags: str | None = None  # JSON array
    embedding: bytes | None = None
    created_at: str = Field(default_factory=lambda: _now())
    updated_at: str = Field(default_factory=lambda: _now())
    metadata: str | None = None


class Task(_DomainModel):
    id: str = Field(default_factory=lambda: _uuid())
    journey: str | None = None
    title: str
    status: str = "todo"  # 'todo', 'doing', 'done', 'blocked'
    due_date: str | None = None  # ISO date (YYYY-MM-DD)
    scheduled_at: str | None = None  # ISO datetime (YYYY-MM-DDTHH:MM) for fixed-time items
    time_hint: str | None = None  # free text such as "late afternoon" or "morning"
    stage: str | None = None  # stage/cycle within the journey
    context: str | None = None
    source: str = "manual"  # 'manual', 'journey_path', 'conversation', 'week_plan'
    created_at: str = Field(default_factory=lambda: _now())
    updated_at: str = Field(default_factory=lambda: _now())
    completed_at: str | None = None
    metadata: str | None = None


class ExtractedWeekItem(_DomainModel):
    """Item extracted from a weekly plan."""

    title: str
    due_date: str  # YYYY-MM-DD, always resolved by the LLM
    scheduled_at: str | None = None  # YYYY-MM-DDTHH:MM for fixed-time items
    time_hint: str | None = None  # "morning", "afternoon", "late afternoon", etc.
    journey: str | None = None
    context: str | None = None


class ExtractedMemory(_DomainModel):
    """Memory extracted by the LLM before id and embedding are assigned."""

    title: str
    content: str
    context: str | None = None
    memory_type: str
    layer: str = "ego"
    tags: list[str] = Field(default_factory=list)
    journey: str | None = None
    persona: str | None = None


class SearchResult(NamedTuple):
    """Search result supporting attributes and tuple unpacking."""

    memory: "Memory"
    score: float


def _uuid() -> str:
    import uuid

    return uuid.uuid4().hex[:8]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
