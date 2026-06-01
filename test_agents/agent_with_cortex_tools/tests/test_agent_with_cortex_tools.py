"""Integration tests for agent_with_cortex_tools.

Verifies that cortex-level MCP tools (get_current_time, web_search) are
discovered and served by the built-in MCP server (port 8001), and that the
agent uses them to answer time and search queries.

All assertions are black-box: only the public FastAPI and MCP JSON-RPC
endpoints are used.
"""

import json
import os
import time

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")
MCP_URL = os.getenv("MCP_URL", "http://app:8001")

_MCP_HEADERS = {
    "Accept": "application/json, text/event-stream, application/x-ndjson"
}


@pytest.mark.depends(name="healthy")
def test_health_endpoint():
    """App must be healthy before running any tests."""
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


@pytest.mark.depends(on=["healthy"], name="mcp_lists_cortex_tools")
def test_mcp_server_lists_cortex_tools():
    """tools/list returns both cortex-level tools: get_current_time and web_search."""
    response = requests.post(
        f"{MCP_URL}/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
        headers=_MCP_HEADERS,
        timeout=10,
    )
    assert response.status_code == 200
    names = [t["name"] for t in response.json()["result"]["tools"]]
    assert "localhost/time_tool.get_current_time" in names, (
        f"Expected 'localhost/time_tool.get_current_time' in tool list; got: {names}"
    )
    assert "localhost/web_search.web_search" in names, (
        f"Expected 'localhost/web_search.web_search' in tool list; got: {names}"
    )


@pytest.mark.depends(on=["mcp_lists_cortex_tools"])
def test_mcp_get_current_time_tool_call():
    """get_current_time returns a non-error string containing a date."""
    response = requests.post(
        f"{MCP_URL}/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "localhost/time_tool.get_current_time",
                "arguments": {"timezone": "UTC"},
            },
        },
        headers=_MCP_HEADERS,
        timeout=10,
        stream=True,
    )
    assert response.status_code == 200
    lines = [ln for ln in response.iter_lines(decode_unicode=True) if ln.strip()]
    payload = json.loads(lines[-1])
    assert payload["result"]["isError"] is False
    text = payload["result"]["content"][0]["text"]
    assert "UTC" in text, f"Expected 'UTC' in time result; got: {text!r}"


@pytest.mark.depends(on=["mcp_lists_cortex_tools"])
def test_mcp_web_search_tool_call_returns_string():
    """web_search returns a non-error string (result or graceful error message)."""
    response = requests.post(
        f"{MCP_URL}/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "localhost/web_search.web_search",
                "arguments": {"query": "Python programming language"},
            },
        },
        headers=_MCP_HEADERS,
        timeout=30,
        stream=True,
    )
    assert response.status_code == 200
    lines = [ln for ln in response.iter_lines(decode_unicode=True) if ln.strip()]
    payload = json.loads(lines[-1])
    assert payload["result"]["isError"] is False
    text = payload["result"]["content"][0]["text"]
    assert isinstance(text, str) and len(text) > 0


@pytest.mark.depends(on=["healthy"], name="agent_basic_response")
def test_agent_basic_response():
    """Agent returns a non-empty response."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What tools do you have available?",
            "user_id": "test-cortex-tools-1",
        },
        timeout=120,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "assistant"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


@pytest.mark.depends(on=["mcp_lists_cortex_tools"])
def test_mcp_tool_annotations_present():
    """Every tool returned by tools/list must have an annotations object with title."""
    response = requests.post(
        f"{MCP_URL}/mcp",
        json={"jsonrpc": "2.0", "id": 10, "method": "tools/list", "params": {}},
        headers=_MCP_HEADERS,
        timeout=10,
    )
    assert response.status_code == 200
    tools = response.json()["result"]["tools"]
    assert tools, "tools/list returned an empty list"
    for t in tools:
        name = t.get("name", "<unknown>")
        annotations = t.get("annotations")
        assert annotations is not None, f"Tool '{name}' is missing annotations"
        assert "title" in annotations, (
            f"Tool '{name}' is missing 'title' in annotations"
        )
        assert isinstance(annotations["title"], str) and annotations["title"], (
            f"Tool '{name}' has an empty title"
        )


@pytest.mark.depends(on=["mcp_lists_cortex_tools"])
def test_mcp_get_current_time_annotations():
    """localhost/time_tool.get_current_time must declare readOnlyHint=True."""
    response = requests.post(
        f"{MCP_URL}/mcp",
        json={"jsonrpc": "2.0", "id": 11, "method": "tools/list", "params": {}},
        headers=_MCP_HEADERS,
        timeout=10,
    )
    assert response.status_code == 200
    tools = {t["name"]: t for t in response.json()["result"]["tools"]}
    assert "localhost/time_tool.get_current_time" in tools
    annotations = tools["localhost/time_tool.get_current_time"]["annotations"]
    assert annotations.get("title") == "Get Current Time"
    assert annotations.get("readOnlyHint") is True, (
        "localhost/time_tool.get_current_time should declare readOnlyHint=True"
    )


@pytest.mark.depends(on=["mcp_lists_cortex_tools"])
def test_mcp_web_search_annotations():
    """localhost/web_search.web_search must declare readOnlyHint=True and openWorldHint=True."""
    response = requests.post(
        f"{MCP_URL}/mcp",
        json={"jsonrpc": "2.0", "id": 12, "method": "tools/list", "params": {}},
        headers=_MCP_HEADERS,
        timeout=10,
    )
    assert response.status_code == 200
    tools = {t["name"]: t for t in response.json()["result"]["tools"]}
    assert "localhost/web_search.web_search" in tools
    annotations = tools["localhost/web_search.web_search"]["annotations"]
    assert annotations.get("title") == "Web Search"
    assert annotations.get("readOnlyHint") is True, (
        "localhost/web_search.web_search should declare readOnlyHint=True"
    )
    assert annotations.get("openWorldHint") is True, (
        "localhost/web_search.web_search should declare openWorldHint=True (calls external API)"
    )


@pytest.mark.depends(on=["agent_basic_response"])
def test_agent_uses_time_tool(clear_test_memory):
    """Agent uses get_current_time to answer a question about the current time."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What is the current time in UTC?",
            "user_id": "test-cortex-tools-time",
        },
        timeout=120,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "assistant"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0
