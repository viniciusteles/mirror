[< CV7.E3 Extraction Quality](../index.md)

# CV7.E3.S3 — Per-conversation summary

**Status:** Done
**Epic:** CV7.E3 — Extraction Quality
**Requires:** CV7.E1 (observability substrate); independent of S1/S2
**Goal:** Replace the naive message-concatenation stored in `Conversation.summary`
with a 3–4 sentence LLM-generated summary. Used by `mm-recall` for display and
as the embedding input for conversation-level semantic search.

---

## What exists today

`_run_extraction()` in `conversation.py` already writes to `Conversation.summary`,
but the content is a blunt truncation of joined message text (2000 chars of raw
content, stored as the first 500 chars). The embedding is generated from that
same raw concatenation. The result is noisy and incoherent — mid-sentence cuts,
repeated filler, no synthesis.

`mm-recall` (cli/recall.py) does not display the summary at all today; it only
shows metadata (title, date, persona, journey) and the message list.

---

## Design

### `CONVERSATION_SUMMARY_PROMPT` (prompts.py)

Static rules. Appended with the formatted transcript at call time — consistent
with how `EXTRACTION_PROMPT` + `format_transcript()` works.

Rules encoded:
- 3–4 sentences of flowing prose (not a list)
- Open with the main topic or question
- Include the key decision, insight, or commitment if one was reached
- Note emotional tone or psychological layer only if clearly present
- Standalone: a reader six months from now must understand the conversation
  from the summary alone; no "we discussed" or "the user said"
- If the conversation is trivial (greetings, scheduling), return an empty string

### `generate_conversation_summary(messages, user_name, on_llm_call)` (extraction.py)

```python
def generate_conversation_summary(
    messages: list[Message],
    user_name: str = "User",
    on_llm_call: Callable[[LLMResponse], None] | None = None,
) -> str:
```

- Returns a plain text string (not JSON)
- Returns `""` on empty messages, LLM error, or trivial conversation
- No JSON parsing — response is used directly after stripping whitespace
- Follows the same `send_to_model` + `on_llm_call` pattern as the other functions

### `SUMMARIZE_ENABLED` flag (config.py)

```python
SUMMARIZE_ENABLED = os.getenv("MEMORY_SUMMARIZE", "") == "1"
```

Default off — existing behavior completely unchanged when unset.

### Wiring into `_run_extraction()` (conversation.py)

Replace the current naive concatenation block with:

```python
if SUMMARIZE_ENABLED:
    summary_text = generate_conversation_summary(
        messages, user_name=user_name, on_llm_call=_make_logger("summary")
    )
    if not summary_text:
        # LLM returned empty (trivial conversation or failure) — fall back.
        summary_text = _naive_summary(messages)
else:
    summary_text = _naive_summary(messages)
```

Extract the existing concatenation logic into a private `_naive_summary(messages)`
helper to keep the branch readable. The embedding and `store.update_conversation`
calls remain identical — they operate on `summary_text` regardless of source.

### `mm-recall` display (cli/recall.py)

Add summary display after the journey line, before the `---` separator:

```
**Summary:** <summary text>
```

Only shown when `conv.summary` is present. No other changes to the recall CLI.

---

## Files changed

| File | Change |
|------|--------|
| `src/memory/intelligence/prompts.py` | Add `CONVERSATION_SUMMARY_PROMPT` |
| `src/memory/config.py` | Add `SUMMARIZE_ENABLED` flag |
| `src/memory/intelligence/extraction.py` | Add `generate_conversation_summary()` |
| `src/memory/services/conversation.py` | Wire into `_run_extraction()`; extract `_naive_summary()` |
| `src/memory/cli/recall.py` | Display summary when present |
| `evals/extraction.py` | Add `conversation-summary` probe (9 probes total) |
| `tests/unit/memory/intelligence/test_extraction.py` | Unit tests for `generate_conversation_summary()` |

---

## Tests

All unit tests mock `send_to_model`.

**`test_extraction.py` additions (`TestGenerateConversationSummary`):**

- Non-empty messages → non-empty string returned
- Empty messages → `""` immediately, no LLM call
- LLM exception → `""` returned (fail safe)
- Response whitespace stripped
- `on_llm_call` invoked with response when LLM is called
- `on_llm_call` not invoked for empty messages

---

## Eval changes (`evals/extraction.py`)

Add `conversation-summary` probe:

- Feed the pricing-decision transcript (substantive conversation with a clear
  decision) to `generate_conversation_summary()`.
- Assert: non-empty string, ≥ 2 sentences (contains at least one `.`),
  ≤ 600 chars, mentions a key topic word (`pric` or `usage`),
  does not contain "we discussed" or "the conversation".

With 9 total probes, THRESHOLD = 0.80 means ≥ 8/9 must pass.

---

## Implementation sequence

```
1. CONVERSATION_SUMMARY_PROMPT — src/memory/intelligence/prompts.py
2. SUMMARIZE_ENABLED — src/memory/config.py
3. generate_conversation_summary() — src/memory/intelligence/extraction.py
4. _naive_summary() + wire into _run_extraction() — conversation.py
5. Summary display in recall CLI — cli/recall.py
6. evals/extraction.py — conversation-summary probe
7. tests — unit tests for generate_conversation_summary()
```

---

## Done condition

- `generate_conversation_summary()` returns a 3–4 sentence string from an LLM call
- Returns `""` on empty messages, LLM failure, or trivial conversation
- When `MEMORY_SUMMARIZE=1`, `_run_extraction()` uses the LLM summary for both
  stored text and embedding; falls back to naive concatenation on empty return
- When `MEMORY_SUMMARIZE=0` (default), behavior identical to before S3
- `mm-recall` displays the summary when present on the conversation row
- `uv run python -m memory eval extraction` passes with ≥ 8/9 (threshold 0.80)
- All unit tests pass in CI without `OPENROUTER_API_KEY`

---

**See also:** [CV7.E3 index](../index.md) · [S2 plan](../cv7-e3-s2-two-pass-extraction/plan.md) · [draft-analysis §5.1](../../draft-analysis.md)
