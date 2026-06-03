"""Pytest configuration and fixtures for Anthropic agent tests."""

import os
import warnings

import pytest
import redis

warnings.filterwarnings("ignore", ".*Pydantic.*", UserWarning)


@pytest.fixture(scope="session")
def anthropic_api_key_available():
    """Check if the ANTHROPIC_API_KEY environment variable is set."""
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        pytest.skip(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Please set it in your .env file to run Anthropic agent tests."
        )

    return True


@pytest.fixture(scope="function")
def clear_test_memory():
    """Clear test conversation memory before test run."""

    redis_host = os.getenv("REDIS_HOST", "redis-test")
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    client = redis.Redis(
        host=redis_host, port=redis_port, decode_responses=False
    )

    def delete_pattern(pattern):
        keys = client.keys(pattern)
        if keys:
            client.delete(*keys)

    def clear_all():
        delete_pattern("memory:test-*")
        delete_pattern("memory:user-*")

    clear_all()
    yield
    clear_all()
