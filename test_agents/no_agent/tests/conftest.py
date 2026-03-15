"""Pytest configuration and fixtures for self-hosted LLM tests."""
import pytest
import os


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


