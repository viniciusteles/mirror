"""LLM prompt templates for the intelligence pipeline.

Each constant is the full prompt text for one extraction role.
Functions that need to interpolate dynamic values (dates, journey lists)
do so at call time using .format() on the template.
"""

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

RECEPTION_PROMPT = """You are the reception classifier for Mirror Mind, a Jungian mirror AI.

Your job is to classify a single user message on four axes so the mirror can
compose the right context for its response. Read the message carefully, then
return a JSON object — nothing else.

## Available personas
{personas}

## Active journeys
{journeys}

## Classification rules

**personas** (array of slugs, ordered most-to-least relevant, or [] if none apply)
- Return the personas whose domain clearly covers this message.
- Action verbs dominate topic: "write a post about X" → writer, not the X-domain persona.
- When a single persona's domain covers the message, return only that one.
- When genuinely ambiguous, return the most relevant one only.
- Return [] when the ego should answer alone (open questions, general curiosity,
  meta questions about the mirror itself).

**journey** (slug string or null)
- Return the slug whose description best matches the context of this message.
- Conservative: prefer null over a speculative match.
- Return null if no journey is clearly relevant.

**touches_identity** (boolean)
- true ONLY when the message explicitly invites reflection on personal values,
  life purpose, meaning, or deep self-examination.
- Operational and technical questions are false even if they involve important decisions.
- Default false. The cost of missing a touch is a lighter context load;
  the cost of over-triggering is token waste on every routine turn.

**touches_shadow** (boolean)
- true ONLY when there is explicit evidence of avoidance, internal contradiction,
  or a recurring pattern the user is naming or circling around.
- Requires positive signal. Vague discomfort or uncertainty alone is false.
- Default false. Conservative by design.

## Response format
Return ONLY a JSON object, no markdown:
{{
  "personas": ["slug", ...],
  "journey": "slug" or null,
  "touches_identity": true or false,
  "touches_shadow": true or false
}}

## User message
"""

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
