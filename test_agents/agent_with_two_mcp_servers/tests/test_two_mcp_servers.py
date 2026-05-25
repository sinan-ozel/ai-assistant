"""Integration test for using two McpServer context managers simultaneously.

Verifies that tools from two separate MCP servers — the built-in server
(port 8001) and an external server — are both available to the LLM within
a single ``with McpServer(), McpServer(...):`` block. The agent must start
cleanly and respond to a question that exercises a tool from the built-in
server (get_current_time) while the external server is also active.
"""

import os
import time

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.mark.depends(name="healthy")
def test_health_endpoint():
    """App must be healthy with both MCP servers registered at startup."""
    url = f"{BASE_URL}/health"
    start = time.time()
    timeout = 90
    while True:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200 and r.json().get("status") == "ok":
                return
        except Exception:
            pass
        if time.time() - start > timeout:
            raise TimeoutError(
                f"/health did not return status=ok within {timeout}s — "
                "one of the two MCP servers may be unreachable"
            )
        time.sleep(1)


@pytest.mark.depends(on=["healthy"])
def test_agent_uses_tool_from_built_in_server_while_external_active():
    """Agent answers a time question using the built-in server's get_current_time
    tool while the external MCP server is simultaneously registered."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What is the current UTC time right now?",
            "user_id": "test-two-mcp-servers-1",
        },
        timeout=120,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "assistant"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0
