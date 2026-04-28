[< CV7.E4 Memory Depth](../index.md)

# CV7.E4.S1 — Hybrid search 2.0 (FTS5 + lexical weight + MMR dedupe)

**Status:** Done
**Epic:** CV7.E4 — Memory Depth: Search, Reinforcement, Shadow
**Requires:** CV7.E1 (eval harness for baseline comparison)
**Goal:** Add FTS5 full-text search as a lexical signal in the hybrid scorer;
add MMR deduplication to suppress near-duplicate results; keep the O(n) semantic
scan for now (sqlite-vec deferred until real scale pressure emerges).

---

## Vector index decision

sqlite-vec is not installed and adding it requires a binary loadable extension
that complicates CI and cross-platform distribution. At current memory pool
sizes (hundreds to low thousands), the in-process cosine scan takes ~10–50ms —
well inside acceptable latency. The architectural win from a vector index is
real but not urgent. Deferred. A future story adds it if measured latency
becomes a problem.

What IS delivered in S1:
- **FTS5 lexical signal** — full-text BM25 ranking via SQLite's built-in
  FTS5 module; no new dependencies.
- **Lexical weight in the hybrid scorer** — FTS5 rank score added alongside
  semantic, recency, reinforcement, relevance. Weights rebalanced.
- **MMR deduplication** — Maximal Marginal Relevance pass after ranking;
  suppresses results whose embedding is too similar to an already-selected
  result. Prevents five memories about the same decision from crowding the top.

---

## Design

### FTS5 table: `memories_fts`

External content table referencing `memories` via its implicit integer rowid:

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    title,
    content,
    context,
    content=memories,
    content_rowid=rowid
);
```

Three triggers on `memories` keep the index in sync:
- `AFTER INSERT` — insert the new row into FTS
- `AFTER UPDATE` — delete old FTS entry, insert updated entry
- `AFTER DELETE` — delete FTS entry

Initial population from existing memories is done in the migration.

### `fts_search(query, memory_type, layer, journey, limit)` (MemoryStore)

Returns `list[tuple[str, float]]` — `(memory_id, rank_score)` pairs, where
`rank_score = 1/(1 + rank)` (1.0 for first result, 0.5 for second, etc.).

- Converts the query to a safe FTS5 expression: each whitespace-delimited word
  is individually double-quoted, giving an AND-of-terms search.
- Joins back to `memories` to apply structured filters (type, layer, journey).
- Returns `[]` gracefully when the FTS table does not exist or the query fails
  (`sqlite3.OperationalError`).

### Updated `SEARCH_WEIGHTS` (config.py)

```python
SEARCH_WEIGHTS = {
    "semantic": 0.50,   # was 0.60 — reduced to make room for lexical
    "recency": 0.15,    # was 0.20
    "reinforcement": 0.10,
    "relevance": 0.10,
    "lexical": 0.15,    # NEW: FTS5 rank-based score
}
```

### `MMR_DEDUP_THRESHOLD` (config.py)

```python
MMR_DEDUP_THRESHOLD = float(os.getenv("MEMORY_DEDUP_THRESHOLD", "0.92"))
```

A candidate is suppressed if its cosine similarity to any already-selected
result is >= threshold. 0.92 is conservative — only near-identical memories
are suppressed, not loosely related ones.

### `mmr_dedupe(candidates, limit, threshold)` (search.py)

```python
def mmr_dedupe(
    candidates: list[tuple[Memory, float, np.ndarray]],
    limit: int,
    threshold: float,
) -> list[SearchResult]:
```

Iterates candidates in score order. Each candidate is added unless its maximum
cosine similarity to already-selected embeddings exceeds `threshold`. Returns
up to `limit` results.

### Updated `MemorySearch.search()` (search.py)

New flow:

```
1. generate_embedding(query)
2. get_all_memories_with_embeddings() — apply filters
3. fts_search(query, filters) → {id: rank_score}
4. For each memory: score = hybrid_score(sem, rec, access, rel) + lexical * fts
5. Sort by combined score
6. mmr_dedupe(sorted, limit, threshold)
7. log_access for returned memories
```

`get_access_count()` is still called per returned memory (existing behavior,
acceptable for small result sets).

---

## Files changed

| File | Change |
|------|--------|
| `src/memory/db/schema.py` | Add `memories_fts` FTS5 table + 3 triggers |
| `src/memory/db/migrations.py` | Migration 008: create table + populate from existing memories |
| `src/memory/config.py` | Rebalanced `SEARCH_WEIGHTS`; add `MMR_DEDUP_THRESHOLD` |
| `src/memory/storage/memories.py` | Add `fts_search()` |
| `src/memory/intelligence/search.py` | Add `mmr_dedupe()`; update `search()` |
| `tests/unit/memory/intelligence/test_search.py` | Add `mmr_dedupe` unit tests |
| `tests/unit/memory/storage/test_memory_store.py` | Add `fts_search` integration tests |

---

## Tests

**`test_search.py` additions:**

- `mmr_dedupe` with all distinct embeddings → returns `limit` results
- `mmr_dedupe` with two nearly identical embeddings → near-duplicate suppressed
- `mmr_dedupe` with fewer candidates than limit → returns all
- `mmr_dedupe` with empty input → returns `[]`

**`test_memory_store.py` additions (integration, real SQLite):**

- `fts_search` returns results for a matching word
- `fts_search` returns empty list for no match
- `fts_search` respects `layer` filter
- `fts_search` respects `journey` filter
- `fts_search` returns `[]` gracefully on malformed query (OperationalError)
- New memory inserted via `create_memory` is found by subsequent `fts_search`

---

## Implementation sequence

```
1. schema.py — memories_fts table + 3 triggers
2. migrations.py — 008_create_memories_fts
3. config.py — updated SEARCH_WEIGHTS, MMR_DEDUP_THRESHOLD
4. storage/memories.py — fts_search()
5. intelligence/search.py — mmr_dedupe() + updated search()
6. tests — mmr_dedupe unit tests + fts_search integration tests
```

---

## Done condition

- `memories_fts` FTS5 table exists with triggers keeping it in sync
- Migration 008 is idempotent
- `fts_search` returns ranked matches; degrades gracefully when table absent
- `mmr_dedupe` suppresses near-duplicate results above threshold
- `MemorySearch.search()` incorporates both FTS lexical signal and MMR dedupe
- All unit and integration tests pass
- 905 tests → all pass (no regressions)

---

**See also:** [CV7.E4 index](../index.md) · [draft-analysis §5.3](../../draft-analysis.md)
