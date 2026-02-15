"""Pytest configuration and fixtures for self-hosted LLM tests."""
import pytest
import requests
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


@pytest.fixture(scope="session")
def ollama_server_available():
    """Check if the self-hosted Ollama server is reachable.

    This fixture runs once per test session and is available to all tests.
    """
    ollama_host = os.getenv("OLLAMA_HOST")

    if not ollama_host:
        pytest.skip(
            "OLLAMA_HOST environment variable is not set. "
            "Please set it in your .env file (copy from .env.example) "
            "to run self-hosted LLM tests."
        )

    try:
        response = requests.get(f"http://{ollama_host}/api/tags", timeout=2)
        is_available = response.status_code == 200
    except Exception:
        is_available = False

    if not is_available:
        pytest.skip(f"Self-hosted Ollama server at {ollama_host} is not reachable")

    return True
