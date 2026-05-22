"""Pytest fixtures for agent_with_default_tools tests."""

import os
import warnings

import pytest

warnings.filterwarnings("ignore", ".*Pydantic.*", UserWarning)

_REDIS_HOST = os.getenv("REDIS_HOST", "redis-test")
_REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))


@pytest.fixture(scope="function")
def clear_test_memory():
    """Clear test conversation keys in Redis before and after each test."""
    import redis

    client = redis.Redis(
        host=_REDIS_HOST, port=_REDIS_PORT, decode_responses=False
    )

    def _clear():
        keys = client.keys("memory:test-default-tools-*")
        if keys:
            client.delete(*keys)

    _clear()
    yield
    _clear()
