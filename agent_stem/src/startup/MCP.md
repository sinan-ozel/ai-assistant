# MCP (Model Context Protocol) Server

The agent-stem container runs a built-in MCP server alongside FastAPI. It exposes
tool functions to the LLM over the standard JSON-RPC 2.0 MCP protocol.

---

## Processes

Three processes run under supervisord:

| Process | Port | Behaviour on failure |
|---------|------|----------------------|
| `mcp_server` | 8001 | `autorestart=false` — crashes terminate the container |
| `fastapi` | 8000 | `autorestart=false` — crashes terminate the container |
| `streamlit` | 8501 | `autorestart=true` — restarts automatically |

The MCP server starts first. FastAPI startup calls `discover_mcp_servers()`, which
connects to `localhost:8001` with 5 retries (3 s delay each). If the MCP server
is still starting when FastAPI boots, the retries cover the window.

---

## Tool Discovery (`common/mcp_tools.py`)

At import time, `mcp_server.py` calls `discover_tools()` with two directories:

```
/app/default/mcp/tools/   — framework defaults (shipped with agent-stem)
/app/cortex/mcp/tools/    — agent-designer tools (mounted at runtime)
```

Every `*.py` file that does not start with `_` is loaded. Every public function
(no `_` prefix) that is **defined in that file** (not an import) becomes an MCP
tool. The tool name is the function name.

### Validation rules

The process crashes with a `ValueError` + `logger.error` on any violation:

| Rule | What is checked |
|------|----------------|
| Docstring required | The docstring becomes the tool description shown to the LLM. |
| Type annotation required | Each parameter must be annotated with one of `{str, int, float, bool, dict, list}`. |
| Default value required | Each parameter must have a default; it is used as the example in the schema. |
| Args section required | Each parameter must have a description in the Google-style `Args:` section of the docstring. |
| No nested dicts | Parameters of type `dict` must not have nested dicts in their default value. |

A bad tool in `cortex/mcp/tools/` crashes the MCP server → FastAPI startup fails →
`backend_exit_listener` terminates the container. This is intentional: broken tool
configuration is surfaced immediately rather than silently dropping the tool.

### Schema generation

Each public function is converted to an MCP tool schema:

```json
{
  "name": "library_search",
  "description": "Search the library vector database ...",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "...", "default": "what is Eberron?" },
      "top_k": { "type": "integer", "description": "...", "default": 5 }
    }
  }
}
```

---

## HTTP Protocol (`mcp_server.py`)

All requests are `POST /mcp` with a JSON-RPC 2.0 body.

| Method | Response type | Notes |
|--------|--------------|-------|
| `initialize` | `JSONResponse` | Returns server capabilities and `serverInfo.name = "ai-assistant-mcp"`. |
| `notifications/initialized` | `JSONResponse` | Acknowledged; no-op. |
| `tools/list` | `JSONResponse` | Returns all discovered tool schemas. |
| `tools/call` | `StreamingResponse` (`application/x-ndjson`) | One NDJSON line with the result or error. |

`tools/call` runs the function in the event loop (async functions) or in the default
executor (sync functions), then yields one JSON line:

```jsonl
{"jsonrpc": "2.0", "id": 4, "result": {"content": [{"type": "text", "text": "..."}], "isError": false}}
```

On exception, `isError` is `true` and the text contains the exception message.

---

## Startup Integration (`startup/mcp_startup.py`)

`discover_mcp_servers()` is called from the FastAPI lifespan. It:

1. Reads `cortex/chat/prompt.py` (or `agent.py`) and walks the AST for `McpServer()`
   calls.
2. `McpServer()` with no arguments resolves to `http://localhost:8001` (the built-in
   server). `McpServer("http://host:port")` or `McpServer(os.environ["VAR"])` also
   work.
3. For each URL, runs the MCP handshake (`initialize` → `notifications/initialized`
   → `tools/list`) with 5 retries and a 10 s timeout per request.
4. Saves the discovered tool list to Redis (`memory.mcp_tools`) so the Streamlit UI
   can display them under "External Tools".
5. Raises `RuntimeError` (terminating the process) if any declared server is
   unreachable or returns zero tools.

### `_parse_mcp_response`

Both `mcp_startup.py` and `tools_dsl.py` share this helper. It handles three
content types:

| Content-type | Parsing strategy |
|---|---|
| `application/json` | `response.json()` |
| `text/event-stream` (SSE) | Finds the first `data:` line and parses it. |
| `application/x-ndjson` | Takes the last non-empty line and parses it. |

---

## DSL Integration (`common/tools_dsl.py`)

`make_mcp_server_class(ctx)` returns a `McpServer` class for use in `prompt.py`.

```python
# cortex/chat/prompt.py
with McpServer():          # connects to built-in MCP server (localhost:8001)
    prompt()               # LLM can call any registered tool during this turn

response = prompt()        # subsequent turns also have tool access
```

The `McpServer` context manager:
- Connects to the MCP server, runs the handshake, lists tools.
- Registers each tool so the LLM can call it in the `prompt()` call inside the `with` block.
- Sends `tools/call` requests via httpx. The `Accept` header includes
  `application/x-ndjson` so the built-in server's streaming response is handled.

---

## Crash Propagation Chain

```
Invalid tool file
  → mcp_server.py import fails (ValueError)
    → uvicorn exits nonzero
      → FastAPI startup can't connect to localhost:8001
        → discover_mcp_servers() raises RuntimeError
          → FastAPI lifespan exits nonzero
            → backend_exit_listener kills container
```

---

## Adding a Built-in Tool

1. Create `agent_stem/default/mcp/tools/my_tool.py`.
2. Define one or more public functions with:
   - A Google-style docstring (first paragraph → tool description, `Args:` section → parameter descriptions).
   - Type annotations from `{str, int, float, bool, dict, list}`.
   - A default value for every parameter.
3. Restart the container. The tool appears automatically in `tools/list`.

```python
def greet(name: str = "world") -> str:
    """Return a greeting message.

    Args:
        name: The name to greet.
    """
    return f"Hello, {name}!"
```

---

## Adding an Agent-Designer Tool

Same rules apply. Place the file in `cortex/mcp/tools/my_tool.py`. It is
mounted at `/app/cortex/mcp/tools/` inside the container at runtime and picked
up automatically on the next startup.

If a cortex tool has the same name as a default tool, the cortex tool wins
(it is loaded second and overwrites the default's entry in the tools dict).
