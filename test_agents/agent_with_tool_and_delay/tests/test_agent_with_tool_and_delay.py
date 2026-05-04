"""Integration tests for agent_with_tool_and_delay.

Verifies that the DSL `delay()` primitive actually pauses execution between
the tool-selection LLM call and the final llm() call.  The prompt configures
a 2-second delay, so the round-trip time must be at least that long.
"""

import os
import time

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")
DELAY_SECONDS = 5


@pytest.mark.depends(name="healthy")
def test_health_endpoint():
    response = requests.get(f"{BASE_URL}/health", timeout=10)
    assert response.status_code == 200


@pytest.mark.depends(on="healthy", name="test_delay_response")
def test_agent_responds():
    """Agent returns a valid non-empty response."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={"message": "Tell me about Eberron.", "user_id": "test-delay-1"},
        timeout=120,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


@pytest.mark.depends(on="healthy")
def test_delay_executes():
    """Response time must be at least DELAY_SECONDS, proving delay() ran."""
    start = time.monotonic()
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={"message": "What is Eberron?", "user_id": "test-delay-2"},
        timeout=120,
    )
    elapsed = time.monotonic() - start

    assert response.status_code == 200
    assert elapsed >= DELAY_SECONDS, (
        f"Response took {elapsed:.2f}s — expected at least {DELAY_SECONDS}s "
        f"due to delay() in prompt.py"
    )
