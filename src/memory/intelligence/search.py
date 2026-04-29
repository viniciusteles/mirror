"""Hybrid search: semantic similarity + recency + reinforcement + relevance."""

import math
from datetime import datetime, timezone

import numpy as np

from memory.config import (
    MMR_DEDUP_THRESHOLD,
    RECENCY_HALF_LIFE_DAYS,
    REINFORCEMENT_DECAY_DAYS,
    REINFORCEMENT_RETRIEVAL_WEIGHT,
    REINFORCEMENT_USE_WEIGHT,
    SEARCH_WEIGHTS,
)
from memory.intelligence.embeddings import bytes_to_embedding, generate_embedding
from memory.models import Memory, SearchResult
from memory.storage.store import Store


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    dot = np.dot(a, b)
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    if norm == 0:
        return 0.0
    return float(dot / norm)


def recency_score(created_at: str) -> float:
    """Exponential decay with configurable half-life."""
    try:
        created = datetime.fromisoformat(created_at.rstrip("Z"))
    except ValueError:
        return 0.5
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    days_ago = (now - created).total_seconds() / 86400
    return math.exp(-math.log(2) * days_ago / RECENCY_HALF_LIFE_DAYS)


def reinforcement_score(
    access_count: int,
    use_count: int,
    last_accessed_at: str | None,
) -> float:
    """Honest reinforcement: use vs retrieval with time decay.

    Distinguishes two signals:
    - use_count: how many times the model explicitly drew on this memory in a
      response. Stronger signal, no decay (a used memory remains relevant).
    - access_count: how many times the memory was retrieved (injected into
      context). Weaker signal, decayed by time since last access — a memory
      retrieved once in 2024 should not stay reinforced forever.

    Weights are configurable via REINFORCEMENT_USE_WEIGHT and
    REINFORCEMENT_RETRIEVAL_WEIGHT (see config.py).
    """
    use_signal = min(1.0, use_count / 5.0)

    retrieval_raw = min(1.0, math.log1p(access_count) / 3.0)
    if access_count > 0 and last_accessed_at:
        try:
            last = datetime.fromisoformat(last_accessed_at.rstrip("Z"))
        except ValueError:
            last = None
    else:
        last = None

    if last is not None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        days = max(0.0, (now - last).total_seconds() / 86400)
        decay = math.exp(-math.log(2) * days / REINFORCEMENT_DECAY_DAYS)
        retrieval_signal = retrieval_raw * decay
    else:
        # access_count == 0 → retrieval_raw == 0; no last_accessed_at → no decay applied.
        retrieval_signal = retrieval_raw

    return REINFORCEMENT_USE_WEIGHT * use_signal + REINFORCEMENT_RETRIEVAL_WEIGHT * retrieval_signal


def hybrid_score(
    semantic: float,
    recency: float,
    reinforcement: float,
    relevance: float,
) -> float:
    """Combine signals with configurable weights."""
    w = SEARCH_WEIGHTS
    return (
        w["semantic"] * semantic
        + w["recency"] * recency
        + w["reinforcement"] * reinforcement
        + w["relevance"] * relevance
    )


def mmr_dedupe(
    candidates: list[tuple[Memory, float, np.ndarray]],
    limit: int,
    threshold: float,
) -> list[SearchResult]:
    """Maximal Marginal Relevance deduplication.

    Iterates candidates in score order. A candidate is suppressed when its
    cosine similarity to any already-selected result meets or exceeds `threshold`.
    Returns up to `limit` SearchResult values.
    """
    selected: list[SearchResult] = []
    selected_embeddings: list[np.ndarray] = []

    for mem, score, emb in candidates:
        if selected_embeddings:
            max_sim = max(cosine_similarity(emb, s) for s in selected_embeddings)
            if max_sim >= threshold:
                continue
        selected.append(SearchResult(mem, score))
        selected_embeddings.append(emb)
        if len(selected) >= limit:
            break

    return selected


class MemorySearch:
    def __init__(self, store: Store):
        self.store = store

    def search(
        self,
        query: str,
        limit: int = 5,
        memory_type: str | None = None,
        layer: str | None = None,
        journey: str | None = None,
    ) -> list[SearchResult]:
        """Search memories using hybrid scoring (semantic + lexical + recency + reinforcement)
        with MMR deduplication."""
        query_embedding = generate_embedding(query)

        # Load all memories with embeddings and apply filters.
        all_memories = self.store.get_all_memories_with_embeddings()
        if memory_type:
            all_memories = [m for m in all_memories if m.memory_type == memory_type]
        if layer:
            all_memories = [m for m in all_memories if m.layer == layer]
        if journey:
            all_memories = [m for m in all_memories if m.journey == journey]

        # Lexical pass: FTS5 rank scores keyed by memory id.
        fts_lookup = dict(
            self.store.fts_search(query, memory_type=memory_type, layer=layer, journey=journey)
        )

        # Score every candidate.
        lexical_weight = SEARCH_WEIGHTS.get("lexical", 0.0)
        candidates: list[tuple] = []
        for mem in all_memories:
            if mem.embedding is None:
                continue
            emb = bytes_to_embedding(mem.embedding)
            sem = cosine_similarity(query_embedding, emb)
            rec = recency_score(mem.created_at)
            access_count = self.store.get_access_count(mem.id)
            reinf = reinforcement_score(access_count, mem.use_count, mem.last_accessed_at)
            score = hybrid_score(sem, rec, reinf, mem.relevance_score)
            score += lexical_weight * fts_lookup.get(mem.id, 0.0)
            candidates.append((mem, score, emb))

        candidates.sort(key=lambda x: x[1], reverse=True)

        # MMR deduplication.
        results = mmr_dedupe(candidates, limit=limit, threshold=MMR_DEDUP_THRESHOLD)

        # Log access for returned memories.
        for sr in results:
            self.store.log_access(sr.memory.id, context=query[:200])

        return results
