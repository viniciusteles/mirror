"""Automatic memory extraction through an LLM."""

import json

from openai import OpenAI

from memory.config import EXTRACTION_MODEL, OPENROUTER_API_KEY, OPENROUTER_BASE_URL
from memory.models import ExtractedMemory, ExtractedWeekItem, Message

EXTRACTION_PROMPT = """You are the memory system for Mirror Mind, a Jungian mirror AI.

Analyze the conversation below and extract meaningful memories. Each memory
must be worth remembering in future conversations.

## Memory Types
- **decision**: An operational or strategic decision
- **insight**: A new realization or understanding
- **idea**: A proposal or concept for future implementation
- **journal**: A journal-like record of emotional state, reflection, or lived experience
- **tension**: Psychological tension, internal conflict, or dilemma
- **learning**: Something learned, technical, personal, or relational
- **pattern**: A recurring observed pattern
- **commitment**: A commitment made by the user
- **reflection**: A deeper reflection about identity or purpose

## Jungian Layers
- **self**: Deep realizations about identity, purpose, and core values
- **ego**: Operational decisions, strategy, and day-to-day knowledge
- **shadow**: Tensions, avoided themes, blind spots, and resistances

## Rules
- Extract 0 to 5 memories, only what is truly meaningful
- Each memory needs a concise title and standalone content
- The "context" field should capture the conversation context that produced the memory
- Tags should be useful keywords for future search
- If the conversation is trivial or too technical to matter as memory, return an empty list

## Response Format
Return ONLY a JSON array, with no markdown:
[
  {
    "title": "...",
    "content": "...",
    "context": "...",
    "memory_type": "...",
    "layer": "...",
    "tags": ["...", "..."],
    "journey": "..." or null,
    "persona": "..." or null
  }
]

If there are no meaningful memories, return: []

## Conversation
"""


JOURNAL_CLASSIFICATION_PROMPT = """You are the memory system for Mirror Mind, a Jungian mirror AI.

Analyze this journal entry and classify it. Return ONLY a JSON object, with no markdown:

{
  "title": "concise title capturing the essence of the entry, max 10 words",
  "layer": "self or ego or shadow",
  "tags": ["tag1", "tag2", "..."]
}

## Jungian Layer Criteria
- **self**: Deep identity, purpose, core values, or meaning of life
- **ego**: Day-to-day operational state, practical frustrations, work/routine reflections
- **shadow**: Unresolved tensions, fears, repeating patterns, avoided themes, vulnerability

## Tag Rules
- 3 to 6 emotional or thematic tags for future search
- Use words that capture the feeling, not only the topic
- Examples: anxiety, gratitude, solitude, clarity, exhaustion, purpose, fear, hope

## Journal Entry
"""


TASK_EXTRACTION_PROMPT = """You are the task management system for Mirror Mind.

Analyze the conversation below and identify commitments, next actions, or tasks
the user accepted or needs to do.

## Rules
- Extract only concrete, actionable commitments, not vague ideas
- Ignore tasks already completed in the conversation
- Each task should have a short actionable title
- If a date is mentioned, extract it as YYYY-MM-DD
- If a journey is associated with the task, include its slug
- If there are no tasks, return an empty list
- Maximum 5 tasks per conversation

## Response Format
Return ONLY a JSON array, with no markdown:
[
  {
    "title": "...",
    "due_date": "YYYY-MM-DD" or null,
    "journey": "slug" or null,
    "stage": "stage/cycle" or null,
    "context": "brief context for where the task came from"
  }
]

If there are no tasks, return: []

## Conversation
"""


class ExtractedTask:
    """Task extracted by the LLM."""

    def __init__(
        self,
        title: str,
        due_date=None,
        journey=None,
        stage=None,
        context=None,
    ):
        self.title = title
        self.due_date = due_date
        self.journey = journey
        self.stage = stage
        self.context = context


def format_transcript(messages: list[Message], user_name: str = "User") -> str:
    """Format messages as a readable transcript."""
    lines = []
    for msg in messages:
        role = user_name if msg.role == "user" else "Mirror"
        lines.append(f"**{role}:** {msg.content}")
    return "\n\n".join(lines)


def extract_memories(
    messages: list[Message],
    persona: str | None = None,
    journey: str | None = None,
    user_name: str = "User",
) -> list[ExtractedMemory]:
    """Extract memories from a conversation using an LLM through OpenRouter."""
    if not messages:
        return []

    transcript = format_transcript(messages, user_name=user_name)
    prompt = EXTRACTION_PROMPT + transcript

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )

    response = client.chat.completions.create(
        model=EXTRACTION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    raw = (response.choices[0].message.content or "").strip()

    # Clean possible markdown wrapping.
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    memories = []
    for item in data:
        try:
            mem = ExtractedMemory(**item)
            # Fill persona/journey when the LLM omitted them.
            if not mem.persona and persona:
                mem.persona = persona
            if not mem.journey and journey:
                mem.journey = journey
            memories.append(mem)
        except Exception:
            continue

    return memories


def extract_tasks(
    messages: list[Message],
    journey: str | None = None,
    user_name: str = "User",
) -> list[ExtractedTask]:
    """Extract tasks from a conversation using an LLM through OpenRouter."""
    if not messages:
        return []

    transcript = format_transcript(messages, user_name=user_name)
    prompt = TASK_EXTRACTION_PROMPT + transcript

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )

    response = client.chat.completions.create(
        model=EXTRACTION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    raw = (response.choices[0].message.content or "").strip()

    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    tasks = []
    for item in data:
        try:
            task = ExtractedTask(
                title=item["title"],
                due_date=item.get("due_date"),
                journey=item.get("journey") or journey,
                stage=item.get("stage"),
                context=item.get("context"),
            )
            tasks.append(task)
        except (KeyError, TypeError):
            continue

    return tasks


WEEK_PLAN_PROMPT = """You are the temporal planning system for Mirror Mind.

Analyze the text below and extract ALL temporal items: tasks, commitments,
events, and meetings.

## Reference Date
Today is {today} ({weekday}).

## Active Journeys
{journeys}

## Extraction Rules

1. **due_date** (required): Resolve ALL relative time references to absolute dates (YYYY-MM-DD).
   - "today" -> {today}
   - "tomorrow" -> the next day
   - "Friday" -> the next Friday from today
   - etc.

2. **scheduled_at**: Use ONLY when an exact time is mentioned, such as "at 7pm" or "15:00".
   Format: YYYY-MM-DDTHH:MM. DO NOT INVENT TIMES.

3. **time_hint**: Use for vague time references such as "late afternoon", "during the day", "morning", or "afternoon".
   If scheduled_at is present, time_hint is null.

4. **journey**: Associate the most likely active journey slug using the list above.
   If there is no clear match, use null.

5. **title**: Short and actionable. If the item is tentative, include "(tentative)" in the title.

6. **context**: Brief context note extracted from the original text.

## Response Format
Return ONLY a JSON array, with no markdown:
[
  {{
    "title": "...",
    "due_date": "YYYY-MM-DD",
    "scheduled_at": "YYYY-MM-DDTHH:MM" or null,
    "time_hint": "..." or null,
    "journey": "slug" or null,
    "context": "..."
  }}
]

If there are no items, return: []

## Text
"""


def extract_week_plan(
    text: str,
    journey_context: list[dict],
) -> list[ExtractedWeekItem]:
    """Extract temporal items from a natural-language weekly plan."""
    from datetime import datetime

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    weekdays = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    weekday = weekdays[now.weekday()]

    journeys_text = (
        "\n".join(f"- **{t['slug']}**: {t['description'][:100]}" for t in journey_context)
        if journey_context
        else "(no active journeys)"
    )

    prompt = (
        WEEK_PLAN_PROMPT.format(
            today=today,
            weekday=weekday,
            journeys=journeys_text,
        )
        + text
    )

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )

    response = client.chat.completions.create(
        model=EXTRACTION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    raw = (response.choices[0].message.content or "").strip()

    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    items = []
    for item_data in data:
        try:
            item = ExtractedWeekItem(**item_data)
            items.append(item)
        except Exception:
            continue

    return items


def classify_journal_entry(content: str) -> dict:
    """Classify a journal entry through an LLM: title, layer, and tags."""
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )

    response = client.chat.completions.create(
        model=EXTRACTION_MODEL,
        messages=[{"role": "user", "content": JOURNAL_CLASSIFICATION_PROMPT + content}],
        temperature=0.3,
    )

    raw = (response.choices[0].message.content or "").strip()

    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"title": content[:60], "layer": "ego", "tags": []}

    return {
        "title": data.get("title", content[:60]),
        "layer": data.get("layer", "ego"),
        "tags": data.get("tags", []),
    }
