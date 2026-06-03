"""Pytest configuration and fixtures for Mistral provider tests."""

import os
import warnings

import pytest
import redis

warnings.filterwarnings("ignore", ".*Pydantic.*", UserWarning)


@pytest.fixture(scope="session")
def mistral_api_key_available():
    """Check if the MISTRAL_API_KEY environment variable is set.

    This fixture runs once per test session and is available to all tests.
    """
    api_key = os.getenv("MISTRAL_API_KEY")

    if not api_key:
        pytest.skip(
            "MISTRAL_API_KEY environment variable is not set. "
            "Please set it in your .env file (copy from .env.example) "
            "to run Mistral provider tests."
        )

    return True


@pytest.fixture(scope="function")
def clear_test_memory():
    """Clear test conversation memory before test run."""

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
