[< CV7.E3 Extraction Quality](../index.md)

# CV7.E3.S4 — Generated descriptors for personas and journeys

**Status:** Done
**Epic:** CV7.E3 — Extraction Quality
**Requires:** CV7.E1 (observability), CV7.E2 (reception uses persona/journey metadata)
**Goal:** Generate short routing-optimized descriptors for personas and journeys;
store them in a sidecar table; reception reads them instead of truncated full content.

---

## The problem

Reception currently routes on `content[:200]` — the first 200 characters of each
persona's or journey's full identity content. Two failure modes:

1. **Truncation noise.** A persona that opens with a long preamble or philosophy
   section before the domain description routes poorly because the first 200 chars
   don't signal what it handles.
2. **Content coupling.** Routing quality is hostage to content formatting. Rewriting
   a persona prompt for voice or depth changes routing behavior as a side effect.

Descriptors decouple the two: content is written for depth and voice; descriptors
are written (and generated) for routing accuracy. Each optimizes for its own purpose.

---

## Design

### `identity_descriptors` sidecar table

```sql
CREATE TABLE identity_descriptors (
    layer        TEXT NOT NULL,
    key          TEXT NOT NULL,
    descriptor   TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    PRIMARY KEY (layer, key)
);
```

`(layer, key)` is the primary key, matching the unique constraint on `identity`.
No foreign key — the sidecar is regenerable independently of the source.

### `IdentityDescriptor` model (models.py)

```python
@dataclass
class IdentityDescriptor:
    layer: str
    key: str
    descriptor: str
    generated_at: str
```

Simple dataclass — no Pydantic needed for a pure-storage read model.

### `DESCRIPTOR_PROMPT` (prompts.py)

Generates a 1-2 sentence routing description. Rules encoded:

- For a **persona**: what domain or type of task this persona handles; written so
  a classifier can match user turns to this persona. Capture the action verbs and
  domains, not the philosophy.
- For a **journey**: what the journey is about and when it is the relevant context
  for a user's message.
- Maximum 150 characters. One or two sentences. Plain text only.
- Do not mention "Mirror Mind", "AI", or meta-system references.

### `generate_descriptor(content, layer, key, on_llm_call)` (extraction.py)

```python
def generate_descriptor(
    content: str,
    layer: str,
    key: str,
    on_llm_call: Callable[[LLMResponse], None] | None = None,
) -> str:
```

- Returns plain text (not JSON); stripped of whitespace.
- Returns `""` on empty content, LLM error, or blank response.
- `layer` and `key` are passed so the prompt can adapt its rules
  (persona vs journey).

### Storage: descriptor methods on `IdentityStore`

```python
def upsert_descriptor(self, layer: str, key: str, descriptor: str) -> None:
    """Insert or replace a descriptor for (layer, key)."""

def get_descriptor(self, layer: str, key: str) -> IdentityDescriptor | None:
    """Return the descriptor for (layer, key), or None if absent."""

def get_descriptors_by_layer(self, layer: str) -> dict[str, str]:
    """Return {key: descriptor} for all descriptors of a given layer."""
```

`get_descriptors_by_layer` is the hot path: one query per layer when building
reception context, instead of N queries per entity.

### Integration in `mirror.py`

In `_resolve_defaults()`, when `RECEPTION_ENABLED` and building `personas_meta`
and `journeys_meta`:

```python
persona_descriptors = mem.store.get_descriptors_by_layer("persona")
journey_descriptors = mem.store.get_descriptors_by_layer("journey")

personas_meta = [
    {
        "slug": ident.key,
        "description": persona_descriptors.get(ident.key) or (ident.content or "")[:200],
        "routing_keywords": meta.get("routing_keywords") or [],
    }
    for ident in raw_personas
]
journeys_meta = [
    {
        "slug": j.key,
        "description": journey_descriptors.get(j.key) or (j.content or "")[:200],
    }
    for j in raw_journeys
]
```

No flag required: descriptors are used when present, fallback to truncated content
when absent. Entities without a descriptor behave exactly as before.

### CLI: `python -m memory descriptor <subcommand>`

```
descriptor generate [--layer LAYER] [--key KEY] [--mirror-home PATH]
    Generate descriptors for personas and journeys (or a specific entity).
    Default (no args): all personas + all journeys.

descriptor list [--layer LAYER] [--mirror-home PATH]
    List stored descriptors.
```

Migration adds the table; CLI populates it on demand.

---

## Files changed

| File | Change |
|------|--------|
| `src/memory/db/schema.py` | Add `identity_descriptors` table |
| `src/memory/db/migrations.py` | `007_create_identity_descriptors` migration |
| `src/memory/models.py` | Add `IdentityDescriptor` dataclass |
| `src/memory/intelligence/prompts.py` | Add `DESCRIPTOR_PROMPT` |
| `src/memory/intelligence/extraction.py` | Add `generate_descriptor()` |
| `src/memory/storage/identity.py` | Add descriptor storage methods |
| `src/memory/skills/mirror.py` | Use descriptors in reception context |
| `src/memory/__main__.py` | Add `descriptor` CLI route |
| `src/memory/cli/descriptor.py` | New: `generate` and `list` subcommands |
| `evals/extraction.py` | Add `descriptor-quality` probe (10 probes total) |
| `tests/unit/memory/intelligence/test_extraction.py` | Unit tests for `generate_descriptor()` |
| `tests/unit/memory/storage/test_identity_descriptor.py` | New: storage contract tests |

---

## Tests

**`test_extraction.py` additions (`TestGenerateDescriptor`):**

- Empty content -> `""`, no LLM call
- Non-empty content -> string returned
- Whitespace stripped from response
- LLM exception -> `""`
- `on_llm_call` invoked when LLM runs
- `on_llm_call` not invoked for empty content

**`test_identity_descriptor.py` (new):**

- `upsert_descriptor` stores a descriptor and `get_descriptor` retrieves it
- `upsert_descriptor` overwrites an existing descriptor (idempotent)
- `get_descriptor` returns `None` for a missing entry
- `get_descriptors_by_layer` returns `{key: descriptor}` for stored entries
- `get_descriptors_by_layer` returns `{}` when none exist for that layer

---

## Eval changes (`evals/extraction.py`)

Add `descriptor-quality` probe:

- Feed the engineer persona content (from the database, or a canned excerpt)
  to `generate_descriptor()`.
- Assert: non-empty, ≤ 200 chars, contains at least one domain word
  (`code`, `engineer`, `technical`, `architecture`, `debug`).

10 total probes, THRESHOLD = 0.80.

---

## Implementation sequence

```
1. schema.py — identity_descriptors table
2. migrations.py — 007_create_identity_descriptors
3. models.py — IdentityDescriptor dataclass
4. prompts.py — DESCRIPTOR_PROMPT
5. extraction.py — generate_descriptor()
6. storage/identity.py — upsert/get/get_by_layer
7. mirror.py — use descriptors in reception context
8. cli/descriptor.py + __main__.py — generate and list commands
9. evals/extraction.py — descriptor-quality probe
10. tests — unit tests for generate_descriptor() and storage
```

---

## Done condition

- `identity_descriptors` table created by migration; schema and migration idempotent
- `generate_descriptor(content, layer, key)` returns a 1-2 sentence routing description
- Returns `""` on empty content or LLM failure
- Descriptors stored via `upsert_descriptor`; retrieved via `get_descriptor` and
  `get_descriptors_by_layer`
- `mirror.py` reception uses stored descriptor when present; falls back to
  `content[:200]` when absent
- `python -m memory descriptor generate` generates and stores descriptors for all
  personas and journeys
- `python -m memory descriptor list` shows stored descriptors
- `uv run python -m memory eval extraction` passes with >= 8/10 (threshold 0.80)
- All unit tests pass in CI without `OPENROUTER_API_KEY`

---

**See also:** [CV7.E3 index](../index.md) · [S3 plan](../cv7-e3-s3-conversation-summary/plan.md) · [draft-analysis §5.2](../../draft-analysis.md)
