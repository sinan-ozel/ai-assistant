"""Integration tests for agent_with_tool_and_delay_on_mistral.

Verifies that a prompt with delay() between tool-selection and the final
llm() call does not trigger a 429 rate-limit response from Mistral.
"""

import os

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.mark.depends(name="healthy")
def test_health_endpoint():
    response = requests.get(f"{BASE_URL}/health", timeout=10)
    assert response.status_code == 200


@pytest.mark.depends(on="healthy")
def test_cortex_tool_names_accepted_by_mistral():
    """Cortex tool names (module__function) must be accepted by Mistral.

    Asks for the current time so the LLM must call get_current_time via the
    internal MCP server.  If tool names use an invalid format (e.g. containing
    '/'), Mistral rejects the request and the agent returns 500.
    """
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What is the current date and time in UTC?",
            "user_id": "test-delay-mistral-toolname",
        },
        timeout=120,
    )
    assert response.status_code == 200, (
        f"Agent returned {response.status_code} — "
        "Mistral may have rejected cortex tool names; check agent logs"
    )
    data = response.json()
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


@pytest.mark.depends(on="healthy")
def test_tool_call_with_delay_does_not_hit_rate_limit():
    """A request that triggers a tool call must not return 429.

    The prompt uses delay() between the tool-selection LLM call and the
    final llm() call.  Without the delay both calls fire in quick succession
    and are likely to exhaust Mistral's per-minute token budget.
    """
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={"message": "Tell me about Eberron.", "user_id": "test-delay-mistral-1"},
        timeout=120,
    )
    assert response.status_code != 429, (
        "Agent returned 429 — delay() did not prevent the rate limit"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0
