"""Pytest configuration and fixtures for Mistral provider tests."""
import pytest
import os


@pytest.fixture(scope="session")
def base_url():
    """Get the base URL for the test environment."""
    return os.getenv("BASE_URL", "http://app:8000")


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
