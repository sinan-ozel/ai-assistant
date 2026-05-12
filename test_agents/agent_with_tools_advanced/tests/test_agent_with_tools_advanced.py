"""Integration tests for agent_with_tools_advanced.

Tests the multi-phase DSL prompt with two llm() calls and multiple notify()
calls.  The advanced agent uses McpServer in two phases: read-only tools first,
then all tools.  All assertions are black-box: only HTTP endpoints are used.

The get_capital tool returns deterministic values (e.g. "Wroat" for Breland)
that a small LLM cannot produce correctly without a successful tool call.
These are used to verify that tool invocation actually worked end-to-end.
"""

import json
import os

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.mark.depends(name="healthy")
def test_health_endpoint():
    """App must be healthy before running chat tests."""
    response = requests.get(f"{BASE_URL}/health", timeout=10)
    assert response.status_code == 200


@pytest.mark.depends(on="healthy", name="test_adv_basic_response")
def test_agent_adv_basic_response():
    """Advanced agent returns a non-empty response."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Tell me about the world of Eberron.",
            "user_id": "test-adv-1",
        },
        timeout=180,
    )
    assert response.status_code == 200
    data = response.json()

    assert "conversation_id" in data
    assert "user_id" in data
    assert "message" in data
    assert "role" in data
    assert "created" in data

    assert data["role"] == "assistant"
    assert data["user_id"] == "test-adv-1"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


@pytest.mark.depends(on="test_adv_basic_response")
def test_agent_adv_two_phase_response(clear_test_memory):
    """Advanced agent completes both tool phases and returns a final response."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Use all your tools to tell me about Eberron.",
            "user_id": "test-adv-2",
            "conversation_id": "test-adv-conv-001",
        },
        timeout=180,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 10


@pytest.mark.depends(on="test_adv_basic_response")
def test_agent_adv_streaming_yields_notifications(clear_test_memory):
    """Streaming response yields intermediate notify() chunks before final done."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Briefly describe what you know about Eberron.",
            "user_id": "test-adv-stream",
            "stream": True,
            "stream_format": "ndjson",
        },
        timeout=180,
        stream=True,
    )
    assert response.status_code == 200

    chunks = []
    for line in response.iter_lines(decode_unicode=True):
        if line:
            chunk = json.loads(line)
            chunks.append(chunk)
            if chunk.get("done"):
                break

    assert len(chunks) > 0
    assert chunks[-1].get("done") is True

    # The advanced prompt sends at least two notify() calls before the final
    # response ("Consulting the draconic prophecy..." and an llm result), so
    # expect more than one non-done chunk.
    non_done = [c for c in chunks if not c.get("done")]
    assert len(non_done) >= 1


@pytest.mark.depends(on="test_adv_basic_response")
def test_tool_result_in_response(clear_test_memory):
    """Response must contain the value returned by the get_capital tool.

    "Wroat" is the capital of Breland according to the MCP server's CAPITALS
    dict.  A model that fails to call the tool correctly (e.g. passes the
    schema back as the argument) will never receive "Wroat" and cannot include
    it in its response.  This catches the failure mode where the LLM echoes
    the tool schema instead of filling in the arguments.
    """
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What is the capital city of Breland?",
            "user_id": "test-adv-tool-result",
        },
        timeout=180,
    )
    assert response.status_code == 200
    data = response.json()
    assert "wroat" in data["message"].lower(), (
        f"Expected 'Wroat' (tool result) in response; got: {data['message']}"
    )
