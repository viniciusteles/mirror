"""Testes das funções puras de busca híbrida."""

import numpy as np
import pytest

from memory.intelligence.search import cosine_similarity, hybrid_score, recency_score


class TestCosineSimilarity:
    def test_identical_vectors_return_one(self):
        a = np.array([1.0, 0.0, 0.0])
        assert cosine_similarity(a, a) == pytest.approx(1.0)

    def test_orthogonal_vectors_return_zero(self):
        a = np.array([1.0, 0.0])
        b = np.array([0.0, 1.0])
        assert cosine_similarity(a, b) == pytest.approx(0.0)

    def test_opposite_vectors_return_minus_one(self):
        a = np.array([1.0, 0.0])
        b = np.array([-1.0, 0.0])
        assert cosine_similarity(a, b) == pytest.approx(-1.0)

    def test_zero_vector_returns_zero(self):
        a = np.zeros(3)
        b = np.array([1.0, 2.0, 3.0])
        assert cosine_similarity(a, b) == 0.0

    def test_both_zero_vectors_return_zero(self):
        assert cosine_similarity(np.zeros(3), np.zeros(3)) == 0.0

    def test_scale_invariant(self):
        a = np.array([1.0, 1.0])
        b = np.array([2.0, 2.0])
        assert cosine_similarity(a, b) == pytest.approx(1.0)

    def test_returns_float(self):
        a = np.array([1.0, 0.5])
        b = np.array([0.5, 1.0])
        result = cosine_similarity(a, b)
        assert isinstance(result, float)


class TestRecencyScore:
    def test_recent_date_returns_high_score(self):
        from datetime import datetime, timedelta, timezone

        recent = (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)).isoformat()
        score = recency_score(recent)
        assert score > 0.9

    def test_old_date_returns_low_score(self):
        score = recency_score("2020-01-01T00:00:00")
        assert score < 0.01

    def test_very_old_date_approaches_zero(self):
        score = recency_score("2000-01-01T00:00:00")
        assert score >= 0.0

    def test_invalid_date_returns_half(self):
        score = recency_score("not-a-date")
        assert score == 0.5

    def test_score_is_between_zero_and_one(self):
        from datetime import datetime, timedelta, timezone

        for days in [0, 7, 30, 365, 3650]:
            date = (
                datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
            ).isoformat()
            score = recency_score(date)
            assert 0.0 <= score <= 1.0, f"Score out of range for {days} days ago: {score}"

    def test_z_suffix_stripped(self):
        from datetime import datetime, timedelta, timezone

        recent = (
            datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)
        ).isoformat() + "Z"
        score = recency_score(recent)
        assert score > 0.9


class TestHybridScore:
    def test_all_max_inputs_return_one(self):
        score = hybrid_score(semantic=1.0, recency=1.0, access_count=0, relevance=1.0)
        assert score <= 1.0

    def test_all_zero_inputs_return_zero(self):
        score = hybrid_score(semantic=0.0, recency=0.0, access_count=0, relevance=0.0)
        assert score == pytest.approx(0.0)

    def test_higher_semantic_yields_higher_score(self):
        low = hybrid_score(semantic=0.1, recency=0.5, access_count=0, relevance=0.5)
        high = hybrid_score(semantic=0.9, recency=0.5, access_count=0, relevance=0.5)
        assert high > low

    def test_higher_access_count_yields_higher_score(self):
        low = hybrid_score(semantic=0.5, recency=0.5, access_count=0, relevance=0.5)
        high = hybrid_score(semantic=0.5, recency=0.5, access_count=100, relevance=0.5)
        assert high > low

    def test_reinforcement_caps_at_one(self):
        # access_count=10^6 should not blow up the score
        score = hybrid_score(semantic=1.0, recency=1.0, access_count=1_000_000, relevance=1.0)
        assert score <= 1.01  # tiny slack for floating point

    def test_returns_float(self):
        result = hybrid_score(0.5, 0.5, 1, 0.5)
        assert isinstance(result, float)
