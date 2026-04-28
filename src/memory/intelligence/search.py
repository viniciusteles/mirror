"""Hybrid search: semantic similarity + recency + reinforcement + relevance."""

import math
from datetime import datetime, timezone

import numpy as np

from memory.config import MMR_DEDUP_THRESHOLD, RECENCY_HALF_LIFE_DAYS, SEARCH_WEIGHTS
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


def hybrid_score(
    semantic: float,
    recency: float,
    access_count: int,
    relevance: float,
) -> float:
    """Combine signals with configurable weights."""
    w = SEARCH_WEIGHTS
    reinforcement = min(1.0, math.log1p(access_count) / 3.0)
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
            score = hybrid_score(sem, rec, access_count, mem.relevance_score)
            score += lexical_weight * fts_lookup.get(mem.id, 0.0)
            candidates.append((mem, score, emb))

        candidates.sort(key=lambda x: x[1], reverse=True)

        # MMR deduplication.
        results = mmr_dedupe(candidates, limit=limit, threshold=MMR_DEDUP_THRESHOLD)

        # Log access for returned memories.
        for sr in results:
            self.store.log_access(sr.memory.id, context=query[:200])

        return results
