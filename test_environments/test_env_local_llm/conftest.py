"""Pytest configuration and fixtures for local LLM tests."""
# No special fixtures needed for this environment
# The Ollama server runs as a container in docker-compose

import os

import pytest


@pytest.fixture(scope="session")
def base_url():
    """Get the base URL for the test environment."""
    return os.getenv("BASE_URL", "http://app:8000")