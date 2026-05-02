"""DSL support for external tool integration via MCP and other protocols.

Provides the Tools base class and McpServer subclass that enable the DSL to
call external tools, dispatch them concurrently, and incorporate results into
the LLM conversation.

DSL usage example::

    with McpServer("http://server:8000") as tools:
        tools.call_read_only()   # LLM picks read-only tools; dispatches them
        notify("Thinking...")
        tools.wait()             # wait for results; appended to messages
        response = llm()         # LLM sees context + tool results
        notify(response)
"""

import asyncio
import concurrent.futures
import json
import logging
from typing import Callable, Optional

import httpx


def _parse_mcp_response(response: httpx.Response) -> dict:
    """Parse an MCP response that may be JSON or a server-sent event stream."""
    content_type = response.headers.get("content-type", "")
    if "text/event-stream" in content_type:
        for line in response.text.splitlines():
            if line.startswith("data:"):
                return json.loads(line[5:].strip())
        raise RuntimeError("MCP SSE response contained no data line")
    return response.json()

logger = logging.getLogger(__name__)


class DslRunContext:
    """Execution context for interactive DSL scripts.

    Carries the mutable message list, provider state, a reference to the
    running event loop, and a thread-safe notification callback.  Created once
    per request and shared among all tool objects created by the DSL.
    """

    def __init__(
        self,
        messages: list,
        providers_state: dict,
        event_loop: asyncio.AbstractEventLoop,
        notify_fn: Callable[[str], None],
    ):
        self.messages = messages
        self.providers_state = providers_state
        self.event_loop = event_loop
        self.notify_fn = notify_fn
        self.llm_called: bool = False
        self.final_response: Optional[str] = None


class Tools:
    """Base class for tool integration in the DSL.

    Subclasses connect to a specific backend (MCP, OpenAPI, …) and implement
    ``_get_tools_for_llm``, ``_is_read_only``, and ``_invoke_tool``.

    The methods on *this* class handle the LLM coordination and concurrency:

    * ``call_read_only()`` — LLM call + non-blocking dispatch of read-only tools
    * ``call_all()``       — LLM call + non-blocking dispatch of all tools
    * ``wait()``           — block until pending calls finish; append results
    """

    def __init__(self, ctx: DslRunContext):
        self._ctx = ctx
        self._pending: list[tuple[str, concurrent.futures.Future]] = []
        self._executor = concurrent.futures.ThreadPoolExecutor()

    # --- abstract interface for subclasses ---

    def _get_tools_for_llm(self) -> list:
        """Return all available tools in LiteLLM/OpenAI function format."""
        raise NotImplementedError

    def _is_read_only(self, tool: dict) -> bool:
        """Return True if tool is safe to run concurrently (read-only)."""
        raise NotImplementedError

    def _invoke_tool(self, name: str, arguments: dict) -> str:
        """Invoke the named tool and return its text result."""
        raise NotImplementedError

    # --- internal LLM + dispatch logic ---

    def _llm_with_tools(self, tools: list) -> None:
        """Call LLM with *tools* and non-blockingly dispatch resulting
        calls."""
        from common.llm import call_llm_by_model

        logger.debug(
            "Tools._llm_with_tools: calling LLM with %d tool(s)", len(tools)
        )
        coro = call_llm_by_model(
            messages=list(self._ctx.messages),
            providers_state=self._ctx.providers_state,
            tools=tools,
            tool_choice="auto",
        )
        response = asyncio.run_coroutine_threadsafe(
            coro, self._ctx.event_loop
        ).result()

        choice = response.choices[0]
        raw_tool_calls = getattr(choice.message, "tool_calls", None) or []

        assistant_msg: dict = {
            "role": "assistant",
            "content": choice.message.content,
        }
        if raw_tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in raw_tool_calls
            ]
        self._ctx.messages.append(assistant_msg)
        logger.debug(
            "Tools._llm_with_tools: LLM chose %d tool call(s)",
            len(raw_tool_calls),
        )

        for tc in raw_tool_calls:
            try:
                arguments = json.loads(tc.function.arguments)
            except Exception:
                arguments = {}
            fut = self._executor.submit(
                self._invoke_tool, tc.function.name, arguments
            )
            self._pending.append((tc.id, fut))

    # --- public DSL interface ---

    def call_read_only(self) -> None:
        """Call LLM with read-only tools; dispatch tool calls non-blocking.

        Only tools whose backend marks them as concurrency-safe (read-only)
        are included.  For MCP servers this is the ``readOnlyHint``
        annotation.
        """
        all_tools = self._get_tools_for_llm()
        read_only = [t for t in all_tools if self._is_read_only(t)]
        if not read_only:
            logger.info("Tools.call_read_only: no read-only tools available")
            return
        logger.debug("Tools.call_read_only: %d tool(s)", len(read_only))
        self._llm_with_tools(read_only)

    def call_all(self) -> None:
        """Call LLM with all tools; dispatch tool calls non-blocking."""
        all_tools = self._get_tools_for_llm()
        if not all_tools:
            logger.info("Tools.call_all: no tools available")
            return
        logger.debug("Tools.call_all: %d tool(s)", len(all_tools))
        self._llm_with_tools(all_tools)

    def wait(self) -> None:
        """Block until all pending tool calls finish; append results to
        messages."""
        for tool_call_id, fut in self._pending:
            try:
                result = fut.result()
            except Exception as e:
                logger.error(
                    "Tool call %s raised: %s", tool_call_id, e, exc_info=True
                )
                result = f"Error: {e}"
            self._ctx.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": result,
                }
            )
        self._pending.clear()

    def __enter__(self) -> "Tools":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wait()
        return False


class McpServer(Tools):
    """MCP server tool provider for the DSL.

    Connects to one or more MCP servers, fetches the tool list on first use,
    and dispatches tool calls via the MCP JSON-RPC over HTTP protocol.

    Usage::

        with McpServer("http://server:8000") as tools:
            tools.call_read_only()
            tools.wait()
            response = llm()
            notify(response)

    A list of URLs is also accepted::

        with McpServer(["http://server-a:8000", "http://server-b:8000"]) as tools:
            ...

    Whether a tool is read-only is determined by the MCP ``readOnlyHint``
    annotation on each tool.
    """

    _MCP_HEADERS = {"Accept": "application/json, text/event-stream"}

    def __init__(self, url_or_urls, ctx: DslRunContext):
        super().__init__(ctx)
        urls = url_or_urls if isinstance(url_or_urls, list) else [url_or_urls]
        self._urls = [u.rstrip("/") for u in urls]
        self._client = httpx.Client(timeout=30.0, headers=self._MCP_HEADERS)
        self._tools_cache: Optional[list] = None
        self._tool_annotations: dict = {}
        self._tool_url_map: dict = {}
        self._session_ids: dict = {}

    def _initialize_session(self, base_url: str) -> None:
        """Run the MCP lifecycle handshake for *base_url*; store session ID."""
        url = f"{base_url}/mcp"
        response = self._client.post(
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
        )
        response.raise_for_status()
        self._session_ids[base_url] = response.headers.get("mcp-session-id")
        self._client.post(
            url,
            json={"jsonrpc": "2.0", "method": "notifications/initialized"},
            headers=self._session_headers(base_url),
        )

    def _session_headers(self, base_url: str) -> dict:
        """Return Mcp-Session-Id header dict if the server assigned one."""
        session_id = self._session_ids.get(base_url)
        return {"Mcp-Session-Id": session_id} if session_id else {}

    def _list_tools_from_server(self, base_url: str) -> list:
        """Run the MCP handshake (if needed) then fetch tool list."""
        if base_url not in self._session_ids:
            self._initialize_session(base_url)
        response = self._client.post(
            f"{base_url}/mcp",
            json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            headers=self._session_headers(base_url),
        )
        response.raise_for_status()
        data = _parse_mcp_response(response)
        if "error" in data:
            raise RuntimeError(f"MCP error from {base_url}: {data['error']}")
        return data.get("result", {}).get("tools", [])

    def _get_tools_for_llm(self) -> list:
        if self._tools_cache is None:
            self._tools_cache = []
            for url in self._urls:
                mcp_tools = self._list_tools_from_server(url)
                for mt in mcp_tools:
                    name = mt["name"]
                    self._tool_url_map[name] = url
                    self._tool_annotations[name] = mt.get("annotations", {})
                    self._tools_cache.append(
                        {
                            "type": "function",
                            "function": {
                                "name": name,
                                "description": mt.get("description", ""),
                                "parameters": mt.get(
                                    "inputSchema",
                                    {"type": "object", "properties": {}},
                                ),
                            },
                        }
                    )
        return self._tools_cache

    def _is_read_only(self, tool: dict) -> bool:
        name = tool.get("function", {}).get("name", "")
        return bool(
            self._tool_annotations.get(name, {}).get("readOnlyHint", False)
        )

    def _invoke_tool(self, name: str, arguments: dict) -> str:
        base_url = self._tool_url_map.get(name, self._urls[0])
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
        logger.info(
            "McpServer: invoking tool %s at %s with args %s",
            name,
            base_url,
            arguments,
        )
        response = self._client.post(
            f"{base_url}/mcp",
            json=payload,
            headers=self._session_headers(base_url),
        )
        response.raise_for_status()
        data = _parse_mcp_response(response)
        if "error" in data:
            return f"Tool error: {data['error']}"
        content = data.get("result", {}).get("content", [])
        if isinstance(content, list):
            return "\n".join(
                block.get("text", "")
                for block in content
                if block.get("type") == "text"
            )
        return str(content)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wait()
        self._client.close()
        return False


def make_mcp_server_class(ctx: DslRunContext):
    """Return a McpServer subclass that injects *ctx* automatically.

    Injected into DSL globals so the script can write::

        with McpServer("http://server:8000") as tools:
            ...

    without passing ``ctx`` explicitly.
    """

    class _McpServer(McpServer):
        def __init__(self, url_or_urls):
            super().__init__(url_or_urls, ctx)

    _McpServer.__name__ = "McpServer"
    _McpServer.__qualname__ = "McpServer"
    return _McpServer


def make_llm_fn(ctx: DslRunContext):
    """Return a ``llm()`` function bound to *ctx*.

    Calling ``llm()`` inside the DSL:

    * Uses the current ``ctx.messages`` as conversation context.
    * Appends the assistant response to ``ctx.messages``.
    * Records ``ctx.llm_called = True`` and stores ``ctx.final_response``.
    * Returns the response text.
    """
    from common.llm import call_llm_by_model

    def llm(input_text: Optional[str] = None) -> str:
        if input_text is not None:
            ctx.messages.append({"role": "user", "content": input_text})
        coro = call_llm_by_model(
            messages=list(ctx.messages),
            providers_state=ctx.providers_state,
        )
        response = asyncio.run_coroutine_threadsafe(
            coro, ctx.event_loop
        ).result()
        assistant_text = response.choices[0].message.content or ""
        ctx.messages.append({"role": "assistant", "content": assistant_text})
        ctx.llm_called = True
        ctx.final_response = assistant_text
        return assistant_text

    return llm


def make_notify_fn(ctx: DslRunContext):
    """Return a ``notify()`` function bound to *ctx*.

    Calling ``notify(text)`` sends *text* to the frontend without adding it
    to the LLM message context.
    """

    def notify(text: str) -> None:
        ctx.notify_fn(str(text))

    return notify
