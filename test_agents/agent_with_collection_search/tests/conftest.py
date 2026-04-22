"""Pytest fixtures for agent_with_collection_search tests."""

import os
import socket

import pytest
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis-test")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant-test")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))


@pytest.fixture
def clear_test_memory():
    """Clear test conversation keys in Redis before and after each test."""
    client = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, decode_responses=False
    )

    def _clear():
        keys = client.keys("memory:test-collection-*")
        if keys:
            client.delete(*keys)

    _clear()
    yield
    _clear()


@pytest.fixture
def chunk_reset(scope='session'):
    """Reset the chunking pipeline state and drop all vector-store collections.

    Clears the Redis chunking state and the library index so every Markdown
    file is treated as new, then deletes all Qdrant collections when Qdrant
    is reachable.
    """
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.delete("memory:chunking_pipeline_state")
    r.delete("memory:library")

    try:
        with socket.create_connection((QDRANT_HOST, QDRANT_PORT), timeout=2):
            qdrant_reachable = True
    except OSError:
        qdrant_reachable = False

    if qdrant_reachable:
        from qdrant_client import QdrantClient

        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        for c in client.get_collections().collections:
            client.delete_collection(c.name)

    yield
