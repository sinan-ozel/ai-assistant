"""Integration tests for the built-in MCP server.

Verifies the server at port 8001 directly using the MCP JSON-RPC protocol —
not via the agent chat endpoint. Tests cover initialization, tool discovery,
schema correctness, streaming tool calls, and error handling.

The MCP server must be reachable from the tests container at
``MCP_URL`` (defaults to ``http://app:8001``). Since FastAPI startup
validates the MCP server before declaring itself healthy, a passing health
check implies the MCP server is up.
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
    """FastAPI must be healthy before MCP tests run.

    A healthy FastAPI implies the MCP server was reachable during startup
    (startup validates it with retries).
    """
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


@pytest.mark.depends(on=["healthy"], name="mcp_initialize")
def test_mcp_server_initialize():
    """MCP initialize handshake returns valid server capabilities."""
    response = requests.post(
        f"{MCP_URL}/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0"},
            },
        },
        headers=_MCP_HEADERS,
        timeout=10,
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("jsonrpc") == "2.0"
    result = data["result"]
    assert result["serverInfo"]["name"] == "ai-assistant-mcp"
    assert "tools" in result["capabilities"]


@pytest.mark.depends(on=["mcp_initialize"], name="mcp_has_search")
def test_mcp_server_lists_search_tool():
    """tools/list returns the built-in 'library_search' tool."""
    response = requests.post(
        f"{MCP_URL}/mcp",
        json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        headers=_MCP_HEADERS,
        timeout=10,
    )
    assert response.status_code == 200
    data = response.json()
    tools = data["result"]["tools"]
    names = [t["name"] for t in tools]
    assert "library_search" in names, (
        f"Expected 'library_search' in tool list; got: {names}"
    )


@pytest.mark.depends(on=["mcp_has_search"])
def test_mcp_server_search_tool_schema():
    """library_search schema has a description, all parameters typed, and defaults."""
    response = requests.post(
        f"{MCP_URL}/mcp",
        json={"jsonrpc": "2.0", "id": 3, "method": "tools/list", "params": {}},
        headers=_MCP_HEADERS,
        timeout=10,
    )
    tools_by_name = {
        t["name"]: t for t in response.json()["result"]["tools"]
    }
    schema = tools_by_name["library_search"]

    assert schema.get("description"), "library_search must have a non-empty description"

    props = schema["inputSchema"]["properties"]
    for param in ("query", "collection", "top_k", "book"):
        assert param in props, (
            f"Expected parameter '{param}' in library_search inputSchema; "
            f"got: {list(props)}"
        )
        assert props[param].get("description"), (
            f"Parameter '{param}' must have a non-empty description"
        )
        assert props[param].get("type"), (
            f"Parameter '{param}' must have a type"
        )
        assert "default" in props[param], (
            f"Parameter '{param}' must have a default (example) value"
        )


@pytest.mark.depends(on=["mcp_has_search"])
def test_mcp_server_tool_call_streams_ndjson():
    """tools/call responds with application/x-ndjson and a valid result payload."""
    response = requests.post(
        f"{MCP_URL}/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "library_search",
                "arguments": {"query": "what is Eberron?"},
            },
        },
        headers=_MCP_HEADERS,
        timeout=30,
        stream=True,
    )
    assert response.status_code == 200
    assert "application/x-ndjson" in response.headers.get("content-type", ""), (
        f"Expected NDJSON content-type; got: {response.headers.get('content-type')}"
    )

    lines = [
        ln for ln in response.iter_lines(decode_unicode=True) if ln.strip()
    ]
    assert lines, "Expected at least one NDJSON line in the response"

    payload = json.loads(lines[-1])
    assert "result" in payload, f"Expected 'result' key in payload; got: {payload}"
    assert isinstance(payload["result"]["content"], list)
    assert payload["result"]["isError"] is False


@pytest.mark.depends(on=["mcp_has_search"])
def test_mcp_server_tool_call_no_results_is_not_error():
    """library_search returns a non-error result even when no documents are indexed."""
    response = requests.post(
        f"{MCP_URL}/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "library_search",
                "arguments": {
                    "query": "obscure topic with no matching documents",
                    "top_k": 3,
                },
            },
        },
        headers=_MCP_HEADERS,
        timeout=30,
        stream=True,
    )
    assert response.status_code == 200
    lines = [
        ln for ln in response.iter_lines(decode_unicode=True) if ln.strip()
    ]
    payload = json.loads(lines[-1])
    assert payload["result"]["isError"] is False
    text = payload["result"]["content"][0]["text"]
    assert isinstance(text, str) and len(text) > 0


@pytest.mark.depends(on=["mcp_initialize"])
def test_mcp_server_unknown_tool_returns_error():
    """tools/call with an unknown tool name returns a 404 error response."""
    response = requests.post(
        f"{MCP_URL}/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {"name": "nonexistent_tool", "arguments": {}},
        },
        headers=_MCP_HEADERS,
        timeout=10,
    )
    assert response.status_code == 404
    data = response.json()
    assert "error" in data, f"Expected 'error' key in response; got: {data}"
    assert data["error"]["code"] == -32601
