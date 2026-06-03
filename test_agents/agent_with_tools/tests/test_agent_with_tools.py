"""Integration tests for agent_with_tools.

Tests that the agent successfully calls MCP tools from the eberron-mcp-server
and incorporates tool results in its response.  All assertions are black-box:
only HTTP endpoints are used.

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


@pytest.mark.depends(on="healthy", name="test_tools_basic_response")
def test_agent_tools_basic_response():
    """Agent returns a non-empty response when MCP tools are available."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Tell me about the world of Eberron.",
            "user_id": "test-tools-1",
        },
        timeout=120,
    )
    assert response.status_code == 200
    data = response.json()

    assert "conversation_id" in data
    assert "user_id" in data
    assert "message" in data
    assert "role" in data
    assert "created" in data

    assert data["role"] == "assistant"
    assert data["user_id"] == "test-tools-1"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


@pytest.mark.depends(on="test_tools_basic_response")
def test_agent_tools_response_uses_tool_context(clear_test_memory):
    """Agent response should reflect information retrieved via MCP tools."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What can you tell me using your available tools?",
            "user_id": "test-tools-2",
            "conversation_id": "test-tools-conv-001",
        },
        timeout=120,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 10


@pytest.mark.depends(on="test_tools_basic_response")
def test_agent_tools_streaming(clear_test_memory):
    """Agent streams response correctly when MCP tools are present."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Briefly describe what you know.",
            "user_id": "test-tools-stream",
            "stream": True,
            "stream_format": "ndjson",
        },
        timeout=120,
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


@pytest.mark.depends(on="healthy")
def test_agent_succeeds_when_llm_skips_tools():
    """Agent must not crash when the LLM decides not to call any tools.

    Regression test for a message-ordering bug: when call_read_only() is
    invoked but the LLM returns no tool calls, a stale assistant message was
    left in the context before llm() ran, causing Mistral (and other providers)
    to reject the request with a 400 'invalid_request_message_order' error.

    A question unrelated to Eberron lore is used to maximise the likelihood
    that the LLM skips tool calls, but the assertion holds either way: the
    agent must return 200 with a non-empty reply regardless of whether tools
    were invoked.
    """
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "How many sides does a triangle have?",
            "user_id": "test-tools-no-tool",
        },
        timeout=120,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


@pytest.mark.depends(on="test_tools_basic_response")
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
            "user_id": "test-tools-tool-result",
        },
        timeout=120,
    )
    assert response.status_code == 200
    data = response.json()
    assert "wroat" in data["message"].lower(), (
        f"Expected 'Wroat' (tool result) in response; got: {data['message']}"
    )
