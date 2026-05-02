"""Pytest configuration and fixtures for agent_with_tools_advanced tests."""

import os
import warnings

import pytest

warnings.filterwarnings("ignore", ".*Pydantic.*", UserWarning)


@pytest.fixture(scope="function")
def clear_test_memory():
    """Clear test conversation memory before and after each test."""
    import redis

    redis_host = os.getenv("REDIS_HOST", "redis-test")
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    client = redis.Redis(host=redis_host, port=redis_port, decode_responses=False)

    def _clear():
        keys = client.keys("memory:test-adv-*")
        if keys:
            client.delete(*keys)

    _clear()
    yield
    _clear()
