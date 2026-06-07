# Tool Calling — Mechanics

This document describes how tool calls flow through the system at runtime.
For DSL syntax and usage examples, see `DSL.md`.

---

## Overview

Tool calling is a two-LLM-call pattern:

1. **Tool-selection call** — the LLM receives the conversation and a list of
   available tool schemas.  It responds with one or more `tool_calls` in the
   assistant message (or none, if it decides no tool is needed).
2. **Tool execution** — the runtime invokes each selected tool concurrently
   in a thread pool and collects the results.
3. **Final call** — the LLM receives the original conversation plus the tool
   results and produces the answer.

---

## Thread model

The DSL script runs inside a `concurrent.futures.ThreadPoolExecutor` thread
(via `loop.run_in_executor`).  The main asyncio event loop runs on the main
thread and handles all async I/O.

Because the DSL thread is synchronous, LLM calls are bridged with
`asyncio.run_coroutine_threadsafe(coro, loop).result()`, which submits the
coroutine to the event loop and blocks the DSL thread until it completes.

Each `McpServer` instance creates its own additional `ThreadPoolExecutor` for
concurrent tool invocations.  Tool HTTP calls run on those threads so they do
not block the event loop or each other.

---

## LLM call flow (inside `prompt()`)

Tool dispatch is handled internally by `prompt()` in `tools_dsl.py`. The DSL
does not call `call_read_only()`, `call_all()`, or `wait()` — those methods do
not exist. The full tool loop runs inside a single `prompt()` call:

```
DSL thread
  │
  └─ prompt()
        │
        ├─ build tool list from all registered McpServer instances
        │     (filtered by _can_handle() — currently all tools from all servers)
        │
        ├─ asyncio.run_coroutine_threadsafe(
        │       asyncio.wait_for(call_llm_by_model(...), timeout=100s),
        │       event_loop
        │   ).result()                            ← blocks DSL thread
        │
        ├─ if response contains tool_calls:
        │     ├─ append assistant message with tool_calls to ctx.messages
        │     ├─ for each tool_call:
        │     │     executor.submit(_invoke_tool, name, args)
        │     │       → collects result, appends tool message to ctx.messages
        │     └─ loop back to LLM call (until no tool_calls in response)
        │
        └─ return final assistant response text
```

`readOnlyHint` and `idempotentHint` are stored in tool schema annotations and
displayed in the Streamlit UI, but they are not used for runtime pre-filtering —
all registered tools are sent to the LLM on every `prompt()` call.

If the LLM returns no tool calls the loop exits immediately and the assistant
message is returned.

---

## MCP protocol

Each `McpServer` maintains one `httpx.Client` (timeout 30 s) shared across
all requests to that server.

On first use the server goes through a handshake:

```
POST /mcp  {"method": "initialize", ...}
  → response headers may contain Mcp-Session-Id

POST /mcp  {"method": "notifications/initialized"}   (no response body needed)

POST /mcp  {"method": "tools/list"}
  → list of tool schemas; cached for the lifetime of the McpServer instance
```

Tool invocations use the same endpoint:

```
POST /mcp  {"method": "tools/call", "params": {"name": "...", "arguments": {...}}}
  → result.content  (list of {"type": "text", "text": "..."} blocks)
```

The session ID (if returned by the server) is sent as `Mcp-Session-Id` on
every subsequent request.  Servers that do not use sessions simply ignore the
header.

Responses may be plain JSON or a server-sent event stream (`text/event-stream`).
The client reads the first `data:` line of an SSE response and parses it as
JSON.

---

## Message list growth

Each tool-calling round appends to `ctx.messages` in this order:

```
[existing messages]
{"role": "assistant", "content": null, "tool_calls": [
    {"id": "call_abc", "type": "function", "function": {"name": "...", "arguments": "..."}},
    ...
]}
{"role": "tool", "tool_call_id": "call_abc", "content": "<result text>"}
...one entry per tool call...
```

The next `llm()` call receives this extended list.  The LLM sees its own
tool-call request and all results before producing its answer.

---

## Timeout chain

```
LLM provider (network)
  ↑ 100 s   asyncio.wait_for in tools_dsl.py
              cancels the LiteLLM coroutine at the event-loop level
              → asyncio.TimeoutError propagates to DSL thread → 500 response

MCP tool HTTP calls
  ↑ 30 s    httpx.Client timeout in McpServer
              → httpx.TimeoutException propagates from _invoke_tool → tool result is an error string

Eval harness → agent endpoint
  ↑ 130 s   requests.post timeout in eval_dsl._send_step
              only reached if the agent endpoint itself hangs (should not happen
              with the 100 s LLM ceiling in place)
```

The 100-second LLM ceiling is deliberately below the 130-second eval HTTP
timeout so the agent can respond with an error before the eval's socket
read-timeout fires.
