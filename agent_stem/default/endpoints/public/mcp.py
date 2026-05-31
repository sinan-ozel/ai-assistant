"""MCP proxy — forwards /mcp requests to the built-in MCP server on port 8001."""

import httpx
from fastapi import Request
from fastapi.responses import Response

_MCP_BACKEND = "http://localhost:8001/mcp"
_TIMEOUT = 180.0


async def handler(request: Request):
    body = await request.body()
    async with httpx.AsyncClient() as client:
        upstream = await client.post(
            _MCP_BACKEND,
            content=body,
            headers={"Content-Type": "application/json"},
            timeout=_TIMEOUT,
        )
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
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
