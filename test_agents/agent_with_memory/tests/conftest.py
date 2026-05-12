"""Pytest fixtures for agent_with_memory tests."""

import os
import socket

import pytest
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis-test")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))


@pytest.fixture
def clear_test_memory():
    """Clear test conversation keys in Redis before and after each test."""
    try:
        with socket.create_connection((REDIS_HOST, REDIS_PORT), timeout=2):
            redis_reachable = True
    except OSError:
        redis_reachable = False

    if not redis_reachable:
        yield
        return

    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)

    def _clear():
        keys = client.keys("memory:test-mem-*")
        if keys:
            client.delete(*keys)

    _clear()
    yield
    _clear()
