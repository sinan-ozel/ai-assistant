"""Pytest configuration and fixtures for Mistral provider tests."""
import pytest
import os


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
    import redis

    redis_host = os.getenv("REDIS_HOST", "redis-test")
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    # Connect to Redis (should be healthy due to depends_on)
    client = redis.Redis(host=redis_host, port=redis_port, decode_responses=False)

    # Clear test-related keys before test
    test_keys = client.keys("memory:test-user-memory:test-memory-conv*")
    if test_keys:
        client.delete(*test_keys)

    yield

    # Clean up after test
    test_keys = client.keys("memory:test-user-memory:test-memory-conv*")
    if test_keys:
        client.delete(*test_keys)