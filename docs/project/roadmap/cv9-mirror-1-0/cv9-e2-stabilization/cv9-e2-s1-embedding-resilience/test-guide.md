[< Story](index.md)

# Test Guide — CV9.E2.S1 Embedding Resilience

## Unit Tests

Add focused tests for `src/memory/intelligence/embeddings.py`.

Expected coverage:

1. **Successful response returns a float32 vector**
   - provider returns one embedding
   - result is a NumPy array
   - dtype is `float32`

2. **Empty response data raises `EmbeddingError`**
   - provider returns `data=[]`
   - no accidental `IndexError`

3. **Missing or empty embedding payload raises `EmbeddingError`**
   - provider returns a data item with no usable embedding

4. **Transient empty response retries and then succeeds**
   - first call returns empty data
   - second call returns a valid embedding
   - final result succeeds
   - provider was called twice

5. **Retry exhaustion raises `EmbeddingError`**
   - all attempts fail
   - final error message is actionable enough to diagnose provider failure

6. **Provider exception is wrapped after retry exhaustion**
   - provider raises an SDK/provider exception
   - final exception is `EmbeddingError`
   - original context is preserved if practical

---

## Service Tests

### MemoryService

Add tests to `tests/unit/memory/services/test_memory.py` or a dedicated module:

- `add_memory` does not call `store.create_memory()` when embedding generation
  raises `EmbeddingError`.
- The store has no new memory row after embedding failure.

### AttachmentService

Add tests to `tests/unit/memory/services/test_attachment.py`:

- `add_attachment` does not call `store.create_attachment()` when embedding
  generation raises `EmbeddingError`.
- The store has no new attachment row after embedding failure.

### Search Paths

Depending on the implementation decision:

- If search fails clearly: memory and attachment search raise `EmbeddingError`
  when query embedding generation fails.
- If memory search falls back to lexical-only: assert the fallback is explicit,
  deterministic, and does not pretend semantic scoring happened.

---

## CLI / Runtime Checks

If CLI-level handling is added, test the relevant command with a mocked failing
embedding boundary or through a narrow CLI unit test.

Expected behavior:

- command exits non-zero
- stderr contains an actionable embedding failure message
- stdout remains clean where runtime hook contracts require stdout purity

---

## Full Verification

Run the standard project checklist:

```bash
uv run pytest
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run pyright src/memory
git diff --check
```

If runtime-facing CLI behavior changes, also run an isolated smoke test with a
temporary DB path:

```bash
DB_PATH=/tmp/mirror-embedding-resilience-smoke.db uv run python -m memory memories --search "test"
```

The exact smoke command may change depending on the touched CLI path. The
important invariant is that production `~/.mirror/<user>/memory.db` is not used
for failure-mode validation.

---

## Regression From The Live Failure

The concrete regression this story protects:

```text
ValueError: No embedding data received
```

After implementation, that condition should become:

```text
EmbeddingError: No embedding data received after <n> attempts
```

or an equivalent domain-level message, with no bad memory/attachment row written.
