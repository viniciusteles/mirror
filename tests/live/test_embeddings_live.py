"""Live test: verify embeddings route correctly through OpenRouter.

Run with:
    uv run pytest tests/live/test_embeddings_live.py -m live -v

Requires OPENROUTER_API_KEY to be set in the environment.
Not included in CI.
"""

import numpy as np
import pytest

from memory.intelligence.embeddings import generate_embedding


@pytest.mark.live
def test_generate_embedding_via_openrouter_returns_correct_shape():
    """Confirm OpenRouter returns a valid 1536-dim float32 embedding."""
    result = generate_embedding("hello world")

    assert isinstance(result, np.ndarray), "result must be a numpy array"
    assert result.dtype == np.float32, f"expected float32, got {result.dtype}"
    assert result.shape == (1536,), f"expected shape (1536,), got {result.shape}"


@pytest.mark.live
def test_generate_embedding_values_are_finite():
    """Confirm no NaN or Inf values in the returned embedding."""
    result = generate_embedding("Mirror Mind is a Jungian AI framework.")
    assert np.all(np.isfinite(result)), "embedding contains NaN or Inf values"


@pytest.mark.live
def test_different_texts_produce_different_embeddings():
    """Confirm the model is actually encoding content, not returning a constant."""
    a = generate_embedding("software engineering and clean code")
    b = generate_embedding("poetry and existential philosophy")
    assert not np.allclose(a, b), "two different texts returned identical embeddings"
