"""MCP proxy — forwards /mcp requests to the built-in MCP server on port 8001."""

import json
from typing import Any, Dict

import httpx
from fastapi.responses import Response

_MCP_BACKEND = "http://localhost:8001/mcp"
_TIMEOUT = 180.0


async def handler(request: Dict[str, Any]):
    body = json.dumps(request).encode()
    async with httpx.AsyncClient() as client:
        upstream = await client.post(
            _MCP_BACKEND,
            content=body,
            headers={"Content-Type": "application/json"},
            timeout=_TIMEOUT,
        )
    # JSON-RPC over HTTP: application-level errors are returned in the body
    # with HTTP 200. Only propagate non-200 status for transport errors.
    status = upstream.status_code
    try:
        data = upstream.json()
        if "error" in data:
            status = 200
    except Exception:
        pass
    return Response(
        content=upstream.content,
        status_code=status,
        media_type=upstream.headers.get("content-type", "application/json"),
    )


spec = {
    "path": "/mcp",
    "methods": ["POST"],
    "summary": "MCP (Model Context Protocol) endpoint",
    "description": (
        "JSON-RPC 2.0 MCP endpoint (HTTP streaming transport). "
        "Proxies to the built-in MCP server. "
        "Supported methods: initialize, notifications/initialized, "
        "tools/list, tools/call."
    ),
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {"type": "object"},
                "example": {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                },
            }
        },
    },
    "responses": {
        200: {
            "description": "MCP JSON-RPC response",
            "content": {
                "application/json": {
                    "schema": {"type": "object"},
                    "example": {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "result": {"tools": []},
                    },
                }
            },
        }
    },
}
