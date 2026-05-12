"""DSL support for external tool integration via MCP and other protocols.

Provides the Tools base class, McpServer subclass, and context-manager
factories (MessageHistory) that enable DSL scripts to call external tools,
limit conversation history, and incorporate results into the LLM conversation.

``prompt()`` is the **only** function in the DSL that calls an LLM.
Registering a tool server via ``McpServer`` makes tool schemas available to
every subsequent ``prompt()`` call; the LLM decides which tools to invoke.
Tool results are collected automatically when the ``with McpServer(...)``
block exits.

DSL usage example::

    with McpServer("http://server:8000"):
        prompt()         # LLM sees tool schemas, selects and dispatches
    # __exit__ calls wait(); tool results are now in ctx.messages
    response = prompt()  # LLM sees full context + tool results
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

_LLM_MAX_RETRIES = 3
_LLM_RETRY_BASE_DELAY = 5.0
# Hard ceiling on a single LLM call. Must be lower than the eval HTTP timeout
# so the agent can return an error before the eval's requests.post read-timeout.
_LLM_CALL_TIMEOUT = 100.0


class DslRunContext:
    """Execution context for one DSL script execution.

    Shared by all Tools objects and the prompt() / notify() callables created
    for the same request.  Carries:

    ``messages``
        Transient message list (history + tool turns).  Mutated only when the
        LLM makes tool calls (assistant tool-call message) and when
        McpServer.__exit__ flushes pending tool results.  Never mutated by
        plain ``prompt()`` text responses.

    ``available_tools``
        Tool schemas registered by active McpServer context managers.
        Offered to the LLM on every ``prompt()`` call while non-empty.

    ``tool_dispatchers``
        Live Tools objects that ``prompt()`` can dispatch tool calls through.

    ``final_response``
        Text of the last ``prompt()`` call, or content of ``print()`` if
        called — returned as the HTTP response body.
    """

    def __init__(
        self,
        messages: list,
        providers_state: dict,
        event_loop: asyncio.AbstractEventLoop,
        notify_fn: Callable[[str], None],
        retry_on_rate_limit: bool = False,
    ):
        self.messages = messages
        self.providers_state = providers_state
        self.event_loop = event_loop
        self.notify_fn = notify_fn
        self.llm_called: bool = False
        self.final_response: Optional[str] = None
        self.retry_on_rate_limit: bool = retry_on_rate_limit
        self.available_tools: list[dict] = []
        self.tool_dispatchers: list["Tools"] = []


class Tools:
    """Base class for tool integration in the DSL.

    Subclasses connect to a specific backend (MCP, OpenAPI, …) and implement
    ``_get_tools_for_llm``, ``_can_handle``, and ``_invoke_tool``.

    On ``__enter__``:

    * Fetches the tool list from the backend.
    * Registers tool schemas into ``ctx.available_tools`` so that subsequent
      ``prompt()`` calls offer them to the LLM.
    * Registers ``self`` into ``ctx.tool_dispatchers`` so that ``prompt()``
      can dispatch tool calls the LLM requests.

    On ``__exit__``:

    * Unregisters own schemas from ``ctx.available_tools``.
    * Removes ``self`` from ``ctx.tool_dispatchers``.
    * Calls ``wait()`` to flush any outstanding tool calls.
    """

    def __init__(self, ctx: DslRunContext):
        self._ctx = ctx
        self._pending: list[tuple[str, concurrent.futures.Future]] = []
        self._executor = concurrent.futures.ThreadPoolExecutor()
        self._registered_tool_names: set[str] = set()

    # --- abstract interface for subclasses ---

    def _get_tools_for_llm(self) -> list:
        """Return all available tools in LiteLLM/OpenAI function format."""
        raise NotImplementedError

    def _can_handle(self, tool_name: str) -> bool:
        """Return True if this dispatcher owns *tool_name*."""
        raise NotImplementedError

    def _invoke_tool(self, name: str, arguments: dict) -> str:
        """Invoke the named tool and return its text result."""
        raise NotImplementedError

    # --- dispatch ---

    def _dispatch(self, tool_call_id: str, tool_name: str, arguments: dict) -> None:
        """Submit *tool_name* to the executor and record the future."""
        fut = self._executor.submit(self._invoke_tool, tool_name, arguments)
        self._pending.append((tool_call_id, fut))

    def wait(self) -> None:
        """Block until all pending tool calls finish; append results to ctx.messages."""
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
        tools = self._get_tools_for_llm()
        self._registered_tool_names = {t["function"]["name"] for t in tools}
        self._ctx.available_tools.extend(tools)
        self._ctx.tool_dispatchers.append(self)
        logger.debug(
            "Tools.__enter__: registered %d tool(s): %s",
            len(tools),
            sorted(self._registered_tool_names),
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._ctx.available_tools = [
            t
            for t in self._ctx.available_tools
            if t["function"]["name"] not in self._registered_tool_names
        ]
        self._ctx.tool_dispatchers = [
            d for d in self._ctx.tool_dispatchers if d is not self
        ]
        self.wait()
        return False


class McpServer(Tools):
    """MCP server tool provider for the DSL.

    Connects to one or more MCP servers, fetches the tool list on first use,
    and dispatches tool calls via the MCP JSON-RPC over HTTP protocol.

    Usage::

        with McpServer("http://server:8000"):
            prompt()         # LLM sees tool schemas; selects and dispatches
        # __exit__ flushes pending calls via wait()
        response = prompt()  # LLM sees full context + tool results

    A list of URLs is also accepted::

        with McpServer(["http://server-a:8000", "http://server-b:8000"]):
            ...
    """

    _MCP_HEADERS = {"Accept": "application/json, text/event-stream"}

    def __init__(self, url_or_urls, ctx: DslRunContext):
        super().__init__(ctx)
        urls = url_or_urls if isinstance(url_or_urls, list) else [url_or_urls]
        self._urls = [u.rstrip("/") for u in urls]
        self._client = httpx.Client(timeout=30.0, headers=self._MCP_HEADERS)
        self._tools_cache: Optional[list] = None
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
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {},
            },
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

    def _can_handle(self, tool_name: str) -> bool:
        return tool_name in self._tool_url_map

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
        self._ctx.available_tools = [
            t
            for t in self._ctx.available_tools
            if t["function"]["name"] not in self._registered_tool_names
        ]
        self._ctx.tool_dispatchers = [
            d for d in self._ctx.tool_dispatchers if d is not self
        ]
        self.wait()
        self._client.close()
        return False


def make_mcp_server_class(ctx: DslRunContext):
    """Return a McpServer subclass that injects *ctx* automatically.

    Injected into DSL globals so the script can write::

        with McpServer("http://server:8000"):
            ...

    without passing ``ctx`` explicitly.
    """

    class _McpServer(McpServer):
        def __init__(self, url_or_urls):
            super().__init__(url_or_urls, ctx)

    _McpServer.__name__ = "McpServer"
    _McpServer.__qualname__ = "McpServer"
    return _McpServer


def make_message_history_class(ctx: DslRunContext):
    """Return a MessageHistory class bound to *ctx*.

    Limits the conversation history visible to ``prompt()`` calls inside the
    block to the last *n* user+assistant turn pairs (2*n messages).  On exit
    the full history is restored, and any messages appended during the block
    (e.g. tool call results) are preserved.

    Usage::

        with MessageHistory(3):
            response = prompt()  # sees only the last 3 turns
    """

    class _MessageHistory:
        def __init__(self, n: int):
            self._n = n

        def __enter__(self):
            # ctx.messages layout: [system, hist1..histN, user_msg]
            # We save and replace msgs[1:-1] (the history slice).
            self._saved_history = ctx.messages[1:-1]
            limited = self._saved_history[-2 * self._n :] if self._n > 0 else []
            ctx.messages[1 : 1 + len(self._saved_history)] = limited
            self._n_limited = len(limited)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            # Replace only the limited history slice; any messages appended
            # after the user message during the block (tool calls, etc.) are
            # preserved because they sit beyond index 1+n_limited.
            ctx.messages[1 : 1 + self._n_limited] = self._saved_history
            return False

    _MessageHistory.__name__ = "MessageHistory"
    _MessageHistory.__qualname__ = "MessageHistory"
    return _MessageHistory


def make_prompt_fn(ctx: DslRunContext):
    """Return the ``prompt()`` callable bound to *ctx*.

    ``prompt()`` is the **only** function in the DSL that calls an LLM.

    Behaviour
    ---------
    * Snapshots ``ctx.messages`` into a local call list.
    * If ``text`` is given, appends it as a user message for this call only.
    * If ``ctx.available_tools`` is non-empty, passes tool schemas with
      ``tool_choice="auto"``.
    * If the LLM response contains tool calls:

      - Appends the full assistant message (including ``tool_calls``) to
        ``ctx.messages`` so that McpServer.__exit__ can match IDs.
      - Dispatches each call through the matching entry in
        ``ctx.tool_dispatchers``.

    * If the LLM response contains no tool calls, ``ctx.messages`` is not
      mutated.
    * Records ``ctx.final_response`` and sets ``ctx.llm_called = True``.
    * Returns the assistant text as a plain ``str``.

    Signature: ``prompt(text=None, provider="default", **kwargs)``

    *text* defaults to ``None`` (use messages already in ctx).  *provider*
    selects a named provider; ``"default"`` uses the configured default.
    Any extra keyword argument is forwarded to LiteLLM as-is (e.g.
    ``temperature=0.9``, ``max_tokens=512``).
    """
    from common.llm import call_llm_by_model

    def prompt(
        text: Optional[str] = None,
        provider: str = "default",
        **kwargs,
    ) -> str:
        import time

        import litellm

        call_messages = list(ctx.messages)
        if text is not None:
            call_messages.append({"role": "user", "content": text})

        requested_model = None if provider == "default" else provider
        tools = ctx.available_tools if ctx.available_tools else None
        if tools:
            kwargs.setdefault("tools", tools)
            kwargs.setdefault("tool_choice", "auto")

        for attempt in range(1, _LLM_MAX_RETRIES + 1):
            coro = call_llm_by_model(
                messages=call_messages,
                providers_state=ctx.providers_state,
                model=requested_model,
                **kwargs,
            )
            try:
                response = asyncio.run_coroutine_threadsafe(
                    asyncio.wait_for(coro, timeout=_LLM_CALL_TIMEOUT),
                    ctx.event_loop,
                ).result()
                break
            except TimeoutError:
                logger.error(
                    "prompt() timed out after %.0fs (attempt %d/%d, model=%r, provider=%r, tools=%d)",
                    _LLM_CALL_TIMEOUT,
                    attempt,
                    _LLM_MAX_RETRIES,
                    requested_model,
                    provider,
                    len(ctx.available_tools),
                )
                raise
            except litellm.RateLimitError:
                if not ctx.retry_on_rate_limit or attempt == _LLM_MAX_RETRIES:
                    raise
                wait = _LLM_RETRY_BASE_DELAY * (2 ** (attempt - 1))
                logger.warning(
                    "LLM rate-limited (attempt %d/%d); retrying in %.0fs.",
                    attempt,
                    _LLM_MAX_RETRIES,
                    wait,
                )
                time.sleep(wait)

        choice = response.choices[0]
        assistant_text = choice.message.content or ""
        raw_tool_calls = getattr(choice.message, "tool_calls", None) or []

        if raw_tool_calls:
            # Persist the full assistant message so McpServer.wait() can match IDs.
            ctx.messages.append(
                {
                    "role": "assistant",
                    "content": choice.message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in raw_tool_calls
                    ],
                }
            )
            for tc in raw_tool_calls:
                try:
                    arguments = json.loads(tc.function.arguments)
                except Exception:
                    arguments = {}
                dispatched = False
                for dispatcher in ctx.tool_dispatchers:
                    if dispatcher._can_handle(tc.function.name):
                        dispatcher._dispatch(tc.id, tc.function.name, arguments)
                        dispatched = True
                        break
                if not dispatched:
                    logger.warning(
                        "prompt(): no dispatcher found for tool '%s'",
                        tc.function.name,
                    )

        ctx.llm_called = True
        ctx.final_response = assistant_text
        return assistant_text

    return prompt


def make_notify_fn(ctx: DslRunContext):
    """Return a ``notify()`` callable bound to *ctx*.

    Calling ``notify(text)`` sends *text* to the frontend immediately without
    adding it to the LLM message context.
    """

    def notify(text: str) -> None:
        ctx.notify_fn(str(text))

    return notify
