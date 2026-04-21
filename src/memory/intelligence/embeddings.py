"""Wrapper for generating embeddings through OpenAI."""

import numpy as np
from openai import OpenAI

from memory.config import EMBEDDING_MODEL, OPENAI_API_KEY


def get_openai_client() -> OpenAI:
    return OpenAI(api_key=OPENAI_API_KEY)


def generate_embedding(text: str) -> np.ndarray:
    """Generate an embedding for text using OpenAI text-embedding-3-small."""
    client = get_openai_client()
    response = client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL,
    )
    return np.array(response.data[0].embedding, dtype=np.float32)


def embedding_to_bytes(embedding: np.ndarray) -> bytes:
    """Convert a numpy array to bytes for SQLite storage."""
    return embedding.astype(np.float32).tobytes()


def bytes_to_embedding(data: bytes) -> np.ndarray:
    """Convert SQLite bytes back to a numpy array."""
    return np.frombuffer(data, dtype=np.float32)
