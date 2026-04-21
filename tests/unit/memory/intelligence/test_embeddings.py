"""Testes das funções de serialização de embeddings."""

import numpy as np

from memory.intelligence.embeddings import bytes_to_embedding, embedding_to_bytes


class TestEmbeddingRoundTrip:
    def test_roundtrip_preserves_values(self):
        original = np.array([0.1, 0.2, 0.3, 0.4, 0.5], dtype=np.float32)
        restored = bytes_to_embedding(embedding_to_bytes(original))
        np.testing.assert_array_almost_equal(original, restored)

    def test_roundtrip_full_dimension(self):
        """Test with realistic 1536-dim embedding."""
        original = np.random.rand(1536).astype(np.float32)
        restored = bytes_to_embedding(embedding_to_bytes(original))
        np.testing.assert_array_almost_equal(original, restored)

    def test_embedding_to_bytes_returns_bytes(self):
        arr = np.array([1.0, 2.0], dtype=np.float32)
        result = embedding_to_bytes(arr)
        assert isinstance(result, bytes)

    def test_bytes_to_embedding_returns_ndarray(self):
        arr = np.array([1.0, 2.0], dtype=np.float32)
        b = embedding_to_bytes(arr)
        result = bytes_to_embedding(b)
        assert isinstance(result, np.ndarray)

    def test_output_dtype_is_float32(self):
        original = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        restored = bytes_to_embedding(embedding_to_bytes(original))
        assert restored.dtype == np.float32

    def test_float64_input_converted_to_float32(self):
        """embedding_to_bytes should coerce float64 → float32."""
        arr64 = np.array([1.0, 2.0, 3.0], dtype=np.float64)
        b = embedding_to_bytes(arr64)
        restored = bytes_to_embedding(b)
        assert restored.dtype == np.float32

    def test_byte_length_matches_float32_size(self):
        n = 128
        arr = np.ones(n, dtype=np.float32)
        b = embedding_to_bytes(arr)
        assert len(b) == n * 4  # 4 bytes per float32

    def test_zero_vector_roundtrip(self):
        original = np.zeros(64, dtype=np.float32)
        restored = bytes_to_embedding(embedding_to_bytes(original))
        np.testing.assert_array_equal(original, restored)

    def test_unit_vector_roundtrip(self):
        original = np.ones(64, dtype=np.float32) / np.sqrt(64)
        restored = bytes_to_embedding(embedding_to_bytes(original))
        np.testing.assert_array_almost_equal(original, restored)
