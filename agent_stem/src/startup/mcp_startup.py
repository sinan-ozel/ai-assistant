"""MCP server startup introspection and tool registration.

At startup, scans ``cortex/chat/prompt.py`` for ``McpServer`` references,
connects to each declared server, and lists its tools.  If any server is
unreachable or returns zero tools the process is terminated — a broken tool
declaration is a configuration error, not a recoverable condition.

Discovered tools are persisted in Redis memory so the Streamlit UI can
display them under "External Tools".
"""

import json
import logging
import re
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_CORTEX_PATH = "/app/cortex"

_MCP_SERVER_PATTERN = re.compile(
    r"""McpServer\(\s*(?:\[)?["\']([^"\']+)["\']""",
    re.MULTILINE,
)


def _extract_mcp_urls(source: str) -> list:
    """Return all MCP server URL string literals found in *source*."""
    return _MCP_SERVER_PATTERN.findall(source)


def _parse_mcp_response(response: httpx.Response) -> dict:
    """Parse an MCP response that may be JSON or a server-sent event stream."""
    content_type = response.headers.get("content-type", "")
    if "text/event-stream" in content_type:
        for line in response.text.splitlines():
            if line.startswith("data:"):
                return json.loads(line[5:].strip())
        raise RuntimeError("MCP SSE response contained no data line")
    return response.json()


def _list_tools(base_url: str) -> list:
    """Run the MCP lifecycle handshake then fetch tools from *base_url*/mcp."""
    url = base_url.rstrip("/") + "/mcp"
    headers = {"Accept": "application/json, text/event-stream"}

    with httpx.Client(timeout=30.0) as client:
        init_response = client.post(
            url,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "ai-assistant", "version": "1.0"},
                },
            },
            headers=headers,
        )
        init_response.raise_for_status()
        session_id = init_response.headers.get("mcp-session-id")
        if session_id:
            headers = {**headers, "Mcp-Session-Id": session_id}

        client.post(
            url,
            json={"jsonrpc": "2.0", "method": "notifications/initialized"},
            headers=headers,
        )

        response = client.post(
            url,
            json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            headers=headers,
        )
        response.raise_for_status()
        data = _parse_mcp_response(response)

    if "error" in data:
        raise RuntimeError(f"MCP error from {base_url}: {data['error']}")
    return data.get("result", {}).get("tools", [])


def _save_tools_to_memory(server_url: str, tools: list) -> None:
    """Persist *tools* in Redis memory keyed by *server_url*."""
    try:
        from redis_memory import Memory

        with Memory() as memory:
            existing = memory.mcp_tools if hasattr(memory, "mcp_tools") else []
            if not isinstance(existing, list):
                existing = []
            entry = {
                "server_url": server_url,
                "tools": [
                    {
                        "name": t.get("name", ""),
                        "description": t.get("description", ""),
                        "read_only": bool(
                            t.get("annotations", {}).get("readOnlyHint", False)
                        ),
                        "destructive": bool(
                            t.get("annotations", {}).get("destructiveHint", False)
                        ),
                        "idempotent": bool(
                            t.get("annotations", {}).get("idempotentHint", False)
                        ),
                        "open_world": bool(
                            t.get("annotations", {}).get("openWorldHint", False)
                        ),
                    }
                    for t in tools
                ],
            }
            existing = [
                e for e in existing if e.get("server_url") != server_url
            ]
            existing.append(entry)
            memory.mcp_tools = existing
        logger.info(
            "MCP startup: saved %d tool(s) for %s to Redis.",
            len(tools),
            server_url,
        )
    except Exception as e:
        logger.warning(
            "MCP startup: could not save tools to Redis (%s). "
            "External tools will not appear in the Streamlit UI.",
            e,
        )


def discover_mcp_servers() -> Optional[list]:
    """Scan cortex/chat/prompt.py for McpServer declarations.

    Returns a list of ``{server_url, tools}`` dicts for every server found,
    or ``None`` if no prompt script exists or it contains no McpServer calls.

    Raises ``RuntimeError`` (causing the process to terminate via the startup
    callback) if any declared server is unreachable or returns zero tools.
    """
    prompt_path = Path(_CORTEX_PATH) / "chat" / "prompt.py"
    if not prompt_path.exists():
        prompt_path = Path(_CORTEX_PATH) / "chat" / "agent.py"
    if not prompt_path.exists():
        logger.debug("MCP startup: no prompt script found; skipping.")
        return None

    try:
        source = prompt_path.read_text(encoding="utf-8")
    except OSError as e:
        logger.error("MCP startup: could not read %s: %s", prompt_path, e)
        return None

    urls = _extract_mcp_urls(source)
    if not urls:
        logger.debug("MCP startup: no McpServer declarations found.")
        return None

    logger.info("MCP startup: found %d McpServer URL(s): %s", len(urls), urls)

    results = []
    for url in urls:
        logger.info("MCP startup: connecting to %s …", url)
        tools = _list_tools(url)
        if not tools:
            raise RuntimeError(
                f"MCP startup: server at {url!r} returned zero tools. "
                "Check the server configuration."
            )
        logger.info(
            "MCP startup: %s — %d tool(s) registered: %s",
            url,
            len(tools),
            [t.get("name") for t in tools],
        )
        _save_tools_to_memory(url, tools)
        results.append({"server_url": url, "tools": tools})

    return results
