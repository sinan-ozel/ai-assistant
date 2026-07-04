"""Integration tests for agent_with_default_tools.

Verifies that the agent correctly integrates with the built-in MCP server
(port 8001) using the default search tool. All assertions are black-box:
only the public FastAPI endpoints are used.

The search tool calls the internal Qdrant/LanceDB backend. Since no documents
are loaded in this test environment, the tool consistently returns a
"no results" message — the tests focus on whether the agent handles that
gracefully, not on retrieval quality.
"""

import json
import os
import time
import uuid

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.mark.depends(name="healthy")
def test_health_endpoint():
    """App must be healthy before running chat tests."""
    url = f"{BASE_URL}/health"
    start = time.time()
    timeout = 60
    while True:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200 and r.json().get("status") == "ok":
                return
        except Exception:
            pass
        if time.time() - start > timeout:
            raise TimeoutError(
                f"/health did not return status=ok within {timeout}s"
            )
        time.sleep(1)


@pytest.mark.depends(on=["healthy"], name="test_basic_response")
def test_agent_basic_response():
    """Agent returns a non-empty response when built-in MCP tools are active."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Hello! What tools do you have available?",
            "user_id": "test-default-tools-1",
        },
        timeout=120,
    )
    assert response.status_code == 200
    data = response.json()

    assert "conversation_id" in data
    assert "user_id" in data
    assert "message" in data
    assert "role" in data

    assert data["role"] == "assistant"
    assert data["user_id"] == "test-default-tools-1"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


@pytest.mark.depends(on=["test_basic_response"])
def test_agent_handles_empty_search_gracefully(clear_test_memory):
    """Agent responds coherently even when the search tool finds no results.

    No documents are indexed in this test environment, so the search tool
    always returns "No relevant documents found." The agent must still produce
    a non-empty reply rather than crashing or returning an error.
    """
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": (
                "According to your knowledge base, "
                "what do you know about the Silver Flame in Eberron?"
            ),
            "user_id": "test-default-tools-2",
        },
        timeout=120,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "assistant"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


@pytest.mark.depends(on=["healthy"])
def test_agent_skips_tools_gracefully():
    """Agent must not crash when the LLM decides not to call any tools.

    Regression: a stale assistant message in the context when the LLM
    returned no tool calls caused 400 message-order errors on some providers.
    A question unrelated to lore maximises the chance the LLM skips tools,
    but the assertion holds either way.
    """
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "How many sides does a hexagon have?",
            "user_id": "test-default-tools-no-tool",
        },
        timeout=120,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


@pytest.mark.depends(on=["test_basic_response"])
def test_agent_streaming(clear_test_memory):
    """Agent streams response correctly when built-in MCP tools are present."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Briefly say hello.",
            "user_id": "test-default-tools-stream",
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

    assert len(chunks) > 0, "Expected at least one streaming chunk"
    assert chunks[-1].get("done") is True


@pytest.mark.depends(on=["test_basic_response"])
def test_agent_multi_turn_with_tools(clear_test_memory):
    """Agent maintains conversation history across turns while using tools."""
    conv_id = f"test-default-tools-multi-turn-{uuid.uuid4()}"

    first = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Search for information about Eberron and tell me what you find.",
            "user_id": "test-default-tools-mt",
            "conversation_id": conv_id,
        },
        timeout=300,
    )
    assert first.status_code == 200
    assert len(first.json()["message"]) > 0

    second = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Based on what you found, what would you suggest I ask next?",
            "user_id": "test-default-tools-mt",
            "conversation_id": conv_id,
        },
        timeout=300,
    )
    assert second.status_code == 200
    data = second.json()
    assert data["role"] == "assistant"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0
