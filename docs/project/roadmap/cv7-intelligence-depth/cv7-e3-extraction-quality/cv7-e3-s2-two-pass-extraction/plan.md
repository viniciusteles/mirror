[< CV7.E3 Extraction Quality](../index.md)

# CV7.E3.S2 — Two-pass extraction (candidate + curate-against-existing)

**Status:** Done
**Epic:** CV7.E3 — Extraction Quality
**Requires:** CV7.E3.S1 (revised extraction prompt)
**Goal:** Add a curation pass that deduplicates candidate memories against the
user's existing memory pool before storing them, so near-duplicates are dropped
or merged rather than accumulated.

---

## The problem

Each conversation is extracted in isolation. Over time, the same insight is
extracted repeatedly — worded slightly differently, stored as a separate memory
— until the pool is diluted by near-duplicates. Search returns five memories
that all say the same thing. The mirror loses precision.

S1 raised the quality bar for what gets extracted. S2 adds deduplication:
before storing candidates, compare them against existing memories and drop (or
merge) anything that's already known.

---

## Design

Two functions, both storage-free:

### `extract_memories()` — unchanged

The existing single-pass function becomes the candidate pass. Its output is a
`list[ExtractedMemory]` — 0 to 3 memories under the S1 quality bar.

### `curate_against_existing(candidates, existing, on_llm_call)` — new

A second LLM call that receives:
- the candidate memories (from `extract_memories()`)
- a compact view of existing similar memories (pre-fetched by the caller)

Returns a filtered/revised `list[ExtractedMemory]` — the same shape as the
extraction output, so the downstream pipeline in `_run_extraction()` does not
change at all.

```python
def curate_against_existing(
    candidates: list[ExtractedMemory],
    existing: list[Memory],
    on_llm_call: Callable[[LLMResponse], None] | None = None,
) -> list[ExtractedMemory]:
```

**Fail-open contract:** on any error (LLM exception, malformed JSON), returns
`candidates` unchanged. The two-pass system degrades gracefully to single-pass
behavior.

**Short-circuit:** if `existing` is empty, returns `candidates` immediately
without an LLM call. No existing pool means nothing to deduplicate against.

### Curation decisions (encoded in the prompt)

- **keep** — genuine new signal not present in existing memories. Include
  unchanged.
- **merge** — meaningfully extends or refines an existing memory. Synthesize a
  combined version using the candidate's structure and the existing memory's
  additional nuance. Include the merged version.
- **drop** — near-duplicate, restatement, or weaker version of an existing
  memory. Omit entirely.

Default: **keep** when uncertain. Only drop on clear overlap. Merge only when
the synthesis is strictly better than either alone. Never invent content.

### `CURATION_PROMPT` constant

Static rules section in `prompts.py`. The function appends dynamic content
(formatted candidates + existing) at call time — consistent with how
`EXTRACTION_PROMPT` + `format_transcript()` works.

### `TWO_PASS_ENABLED` flag

`src/memory/config.py`:
```python
TWO_PASS_ENABLED = os.getenv("MEMORY_TWO_PASS", "") == "1"
```

Default off — existing behavior completely unchanged when unset.

### Wiring into `_run_extraction()` (conversation.py)

After `extract_memories()` produces candidates, when `TWO_PASS_ENABLED`:

1. For each candidate, search existing memories: `title + " " + content[:60]`
   as the query, limit 3, filtered by the conversation's journey.
2. Deduplicate search results by memory id. Cap at 15 total.
3. Call `curate_against_existing(candidates, similar, on_llm_call=_make_logger("curation"))`.
4. Use the returned list for storage.

The `_make_logger("curation")` callback writes `role="curation"` rows to
`llm_calls` when `MEMORY_LOG_LLM_CALLS=1`.

---

## Files changed

| File | Change |
|------|--------|
| `src/memory/intelligence/prompts.py` | Add `CURATION_PROMPT` |
| `src/memory/config.py` | Add `TWO_PASS_ENABLED` flag |
| `src/memory/intelligence/extraction.py` | Add `curate_against_existing()` |
| `src/memory/services/conversation.py` | Wire two-pass into `_run_extraction()` behind flag |
| `evals/extraction.py` | Add `two-pass-dedup` probe |
| `tests/unit/memory/intelligence/test_extraction.py` | Unit tests for `curate_against_existing()` |

---

## Tests

All unit tests mock `send_to_model` — no real LLM, no API key.

**`test_extraction.py` additions:**

- Valid curation response: subset of candidates returned correctly
- Empty candidates → `[]` immediately, no LLM call
- Empty existing → candidates returned unchanged, no LLM call
- All candidates dropped → `[]` returned (trusted curation decision)
- Malformed JSON → candidates returned unchanged (fail open)
- LLM exception → candidates returned unchanged (fail open)
- `on_llm_call` invoked when existing is non-empty and LLM is called
- `on_llm_call` NOT invoked when existing is empty (short-circuit)

---

## Eval changes (`evals/extraction.py`)

Add `two-pass-dedup` probe:

- Build two candidates: one novel decision (pricing model change), one
  near-duplicate of a pre-existing memory (auth module split already in
  the existing pool).
- Build one `Memory` object representing the existing auth-split memory.
- Call `curate_against_existing(candidates, [existing_memory])`.
- Assert: 1 memory returned, it is the novel one (pricing decision), the
  duplicate is dropped.

With 8 total probes, THRESHOLD = 0.80 means ≥ 7/8 must pass.

---

## Implementation sequence

```
1. CURATION_PROMPT — src/memory/intelligence/prompts.py
2. TWO_PASS_ENABLED — src/memory/config.py
3. curate_against_existing() — src/memory/intelligence/extraction.py
4. Wire into _run_extraction() — src/memory/services/conversation.py
5. evals/extraction.py — two-pass-dedup probe
6. tests — unit tests for curate_against_existing()
```

---

## Done condition

- `curate_against_existing(candidates, existing)` returns a deduplicated list
- When `existing` is empty, returns `candidates` unchanged (no LLM call)
- On LLM failure or malformed JSON, returns `candidates` (fail open)
- When `MEMORY_TWO_PASS=1`, `_run_extraction()` runs the curate pass after extract
- When `MEMORY_TWO_PASS=0` (default), behavior is identical to before S2
- `uv run python -m memory eval extraction` passes with ≥ 7/8 (new total; threshold 0.80)
- `MEMORY_LOG_LLM_CALLS=1 MEMORY_TWO_PASS=1` produces a `role="curation"` row in
  `llm_calls` on extraction
- All unit tests pass in CI without `OPENROUTER_API_KEY`

---

**See also:** [CV7.E3 index](../index.md) · [S1 plan](../cv7-e3-s1-extraction-prompt-revision/plan.md) · [draft-analysis §5.1](../../draft-analysis.md)
