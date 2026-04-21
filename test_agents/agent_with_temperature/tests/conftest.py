"""Pytest fixtures for agent_with_temperature tests."""

import os

import pytest
import redis


@pytest.fixture
def clear_test_memory():
    """Clear test conversation keys in Redis before and after each test."""
    redis_host = os.getenv("REDIS_HOST", "redis-test")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    client = redis.Redis(host=redis_host, port=redis_port, decode_responses=False)

    def _clear():
        keys = client.keys("memory:test-temp-*")
        if keys:
            client.delete(*keys)

    _clear()
    yield
    _clear()
