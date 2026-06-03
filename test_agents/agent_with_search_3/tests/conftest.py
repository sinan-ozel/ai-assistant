"""Pytest fixtures for agent_with_search tests."""

import os
import socket

import pytest
import redis
from qdrant_client import QdrantClient

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
        keys = client.keys("memory:test-search-*")
        if keys:
            client.delete(*keys)

    _clear()
    yield
    _clear()


@pytest.fixture(scope='session', autouse=True)
def chunk_reset():
    """Drop Qdrant collections and re-trigger chunking when Qdrant is present.

    Pre-app cleanup (deleting generated .md files and clearing Redis pipeline
    state) is handled by the docker-compose init service, which runs before
    the app container starts.  This fixture only needs to act when Qdrant is
    reachable: it drops the collections that the init service could not reach
    (Qdrant starts after init) and clears pipeline state so the chunking
    pipeline repopulates Qdrant from scratch.

    In environments without Qdrant (e.g. test_env_no_qdrant) the init service
    has already established a clean state and this fixture is a no-op.
    """
    try:
        with socket.create_connection((QDRANT_HOST, QDRANT_PORT), timeout=2):
            qdrant_reachable = True
    except OSError:
        qdrant_reachable = False

    if not qdrant_reachable:
        yield
        return


    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    for c in client.get_collections().collections:
        client.delete_collection(c.name)

    r.delete("memory:chunking_pipeline_state")
    r.delete("memory:library")

    yield
