"""Pytest configuration and fixtures for local LLM tests."""

# No special fixtures needed for this environment
# The Ollama server runs as a container in docker-compose

import os
import warnings

import pytest

warnings.filterwarnings("ignore", ".*Pydantic.*", UserWarning)


@pytest.fixture(scope="session")
def base_url():
    """Get the base URL for the test environment."""
    return os.getenv("BASE_URL", "http://app:8000")


@pytest.fixture(scope="function")
def clear_test_memory():
    """Clear test conversation memory before test run."""
    import redis

    redis_host = os.getenv("REDIS_HOST", "redis-test")
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    # Connect to Redis (should be healthy due to depends_on)
    client = redis.Redis(
        host=redis_host, port=redis_port, decode_responses=False
    )

    def delete_pattern(pattern):
        keys = client.keys(pattern)
        if keys:
            client.delete(*keys)

    def clear_all():
        delete_pattern("memory:test-*")
        delete_pattern("memory:user-alice:*")
        delete_pattern("memory:user-bob:*")

    clear_all()
    yield
    clear_all()
