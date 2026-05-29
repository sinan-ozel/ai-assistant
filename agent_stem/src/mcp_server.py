"""Built-in MCP server — serves default and cortex tools on port 8001.

Discovers Python tool files from two directories at startup:

  /app/default/mcp/tools/   — framework defaults (shipped with agent-stem)
  /app/cortex/mcp/tools/    — agent-designer tools (mounted at runtime)

Every public function defined in those files becomes an MCP tool. Tool
definitions are validated at import time; a missing docstring, type hint,
default value, or field description crashes the process immediately with
an informative log message.

All tool calls are streamed as NDJSON (application/x-ndjson).

MCP protocol — POST /mcp, JSON-RPC 2.0:
  initialize              → server capabilities handshake
  notifications/initialized → acknowledgement (no-op response)
  tools/list              → returns all discovered tool schemas
  tools/call              → invokes a tool, streams result as NDJSON
"""

import asyncio
import inspect
import json
import logging
import os
from pathlib import Path
from typing import AsyncIterator

from common.mcp_tools import discover_tools
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

_log_level = getattr(
    logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO
)
logging.basicConfig(level=_log_level)
logger = logging.getLogger(__name__)

_DEFAULT_TOOLS_DIR = Path("/app/default/mcp/tools")
_CORTEX_TOOLS_DIR = Path("/app/cortex/mcp/tools")

# Discover and validate at import time so startup errors crash immediately.
# Each directory is discovered separately so tools are tagged with their source.
_tools = {
    **discover_tools([_DEFAULT_TOOLS_DIR], source="default"),
    **discover_tools([_CORTEX_TOOLS_DIR], source="cortex"),
}
logger.info("MCP server: %d tool(s) loaded: %s", len(_tools), sorted(_tools))

app = FastAPI(title="ai-assistant-mcp", version="0.1.0")


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    body = await request.json()
    method = body.get("method", "")
    params = body.get("params", {})
    req_id = body.get("id")

    if method == "initialize":
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "ai-assistant-mcp",
                        "version": "0.1.0",
                    },
                },
            }
        )

    if method == "notifications/initialized":
        return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": {}})

    if method == "tools/list":
        tool_list = [schema for _, schema in _tools.values()]
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": tool_list},
            }
        )

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in _tools:
            return JSONResponse(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found.",
                    },
                },
                status_code=404,
            )

        func, _ = _tools[tool_name]
        logger.info(
            "MCP server: calling tool '%s' with args %s", tool_name, arguments
        )
        return StreamingResponse(
            _stream_tool_call(func, arguments, req_id),
            media_type="application/x-ndjson",
        )

    return JSONResponse(
        {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Unknown method '{method}'.",
            },
        },
        status_code=400,
    )


async def _stream_tool_call(
    func, arguments: dict, req_id
) -> AsyncIterator[str]:
    """Invoke *func* with *arguments* and yield the result as one NDJSON
    line."""
    try:
        if inspect.iscoroutinefunction(func):
            result = await func(**arguments)
        else:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: func(**arguments))
    except Exception as exc:
        logger.error("MCP server: tool call failed: %s", exc, exc_info=True)
        yield json.dumps(
            {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"Tool error: {exc}"}],
                    "isError": True,
                },
            }
        ) + "\n"
        return

    yield json.dumps(
        {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": str(result)}],
                "isError": False,
            },
        }
    ) + "\n"
