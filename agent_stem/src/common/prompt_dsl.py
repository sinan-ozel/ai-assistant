"""Python-based DSL for customizable prompt generation.

This module provides a unified runtime for executing user-defined Python scripts
that control prompt construction, model parameters, and conversation behaviour.

Every script goes through the same execution path — there is no interactive vs
non-interactive split.

DSL contract (see agent_stem/src/common/DSL.md for full documentation):

- Module docstring        → system prompt
- prompt(text, ...)       → calls the LLM; returns response text
- print(text)             → sends text as the final response (no LLM call)
- notify(text)            → intermediate streaming message (not saved to history)
- with Search(query, ...) → injects retrieval results into ctx before prompt()
- with MessageHistory(n)  → limits history to last n turn-pairs inside the block
- with McpServer(url)     → registers MCP tool schemas; auto-flushed on exit
- delay(seconds)          → time.sleep alias for pacing LLM calls
- logger                  → pre-configured logging.Logger

Minimal example (``cortex/chat/prompt.py``)::

    \"\"\"You are a helpful assistant.\"\"\"

    response = prompt()

RAG example::

    \"\"\"You are a helpful assistant.\"\"\"

    with Search(input_text):
        response = prompt()

Tool use example::

    \"\"\"You are a knowledgeable guide.\"\"\"

    with McpServer("http://tools:8000"):
        prompt()   # LLM selects and dispatches tools

    response = prompt()   # synthesis — no tool schemas active
"""

import asyncio
import contextlib
import io
import logging
import runpy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from common.search import DEFAULT_TOP_K, run_search

logger = logging.getLogger(__name__)


@dataclass
class PromptResult:
    """Result of executing a DSL script.

    Attributes:
        system_message: System prompt (from module docstring).
        llm_called: True when ``prompt()`` was called by the script.
        final_response: Last response set by ``prompt()`` or ``print()``.
        accumulated_messages: Final messages list after execution.
        full_override: Structured override dict (set via ``_override``).
    """

    system_message: Optional[str] = None
    llm_called: bool = False
    final_response: Optional[str] = None
    accumulated_messages: Optional[list[dict]] = None
    full_override: Optional[dict] = None


class Search:
    """Vector search helper for DSL scripts.

    When used as a context manager, fetches results on ``__enter__`` and
    injects them as a user message into ``ctx.messages`` (before the current
    user query).  On ``__exit__`` the injected message is removed, restoring
    the original message list.  ``prompt()`` calls inside the block
    automatically see the search results.

    When used as a plain value (``str(Search(...))``) it returns the results
    as a formatted string without touching ctx.

    Parameters
    ----------
    query:
        Free-text search query.
    collection:
        Single collection to restrict the search to.  ``None`` searches all.
    top_k:
        Maximum number of results.
    filter:
        Optional equality-filter dict.
    """

    def __init__(
        self,
        query: str,
        collection: Optional[str] = None,
        top_k: int = DEFAULT_TOP_K,
        filter: Optional[dict] = None,
    ):
        logger.debug(
            "Search.__init__: query=%r", query[:80] if query else query
        )
        self._query = query
        self._collection = collection
        self._top_k = top_k
        self._filter = filter
        self._cached: Optional[str] = None
        # Bound ctx — set by make_search_class; None for plain str() usage.
        self._ctx = None
        self._inject_idx: Optional[int] = None

    def _fetch(self) -> str:
        if self._cached is not None:
            return self._cached
        collections = (
            [self._collection] if self._collection is not None else None
        )
        logger.debug(
            "Search._fetch: query=%r collection=%r top_k=%d filter=%r",
            self._query,
            self._collection,
            self._top_k,
            self._filter,
        )
        results = run_search(
            query=self._query,
            collections=collections,
            top_k=self._top_k,
            filter_payload=self._filter,
        )
        logger.debug(
            "Search._fetch: got %d result(s): %s",
            len(results),
            [r.get("file_path", "") for r in results],
        )
        lines = []
        for result in results:
            file_path = result.get("file_path", "")
            section = result.get("section_title", "")
            text = result.get("text", "")
            header_parts = [p for p in [file_path, section] if p]
            if header_parts:
                lines.append(f"[{' | '.join(header_parts)}]")
            if text:
                lines.append(text)
        self._cached = "\n".join(lines)
        return self._cached

    def __str__(self) -> str:
        return self._fetch()

    def __add__(self, other: str) -> str:
        return self._fetch() + other

    def __radd__(self, other: str) -> str:
        return other + self._fetch()

    def __enter__(self) -> "Search":
        logger.debug(
            "Search.__enter__: query=%r",
            self._query[:80] if self._query else self._query,
        )
        results_text = self._fetch()
        if self._ctx is not None:
            # Inject before the last user message (the current user query) so
            # the model sees: [...history, search_results, user_query].
            self._inject_idx = max(0, len(self._ctx.messages) - 1)
            self._ctx.messages.insert(
                self._inject_idx,
                {"role": "user", "content": f"Search results:\n{results_text}"},
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug("Search.__exit__: inject_idx=%s", self._inject_idx)
        if self._ctx is not None and self._inject_idx is not None:
            del self._ctx.messages[self._inject_idx]
        return False


def make_search_class(ctx):
    """Return a Search subclass that injects results into *ctx*.messages."""

    class _Search(Search):
        def __init__(
            self, query, collection=None, top_k=DEFAULT_TOP_K, filter=None
        ):
            super().__init__(query, collection, top_k, filter)
            self._ctx = ctx

    _Search.__name__ = "Search"
    _Search.__qualname__ = "Search"
    return _Search


def _make_input(input_text: str):
    """Return an ``input()`` override that always returns *input_text*."""

    def input(_prompt=""):  # noqa: A001
        return input_text

    return input


def find_prompt_script(cortex_path: str) -> Optional[Path]:
    """Return the path to the prompt DSL script, or ``None`` if not found."""
    if not cortex_path:
        return None
    chat_dir = Path(cortex_path) / "chat"
    if not chat_dir.exists() or not chat_dir.is_dir():
        return None
    for filename in ("prompt.py", "agent.py"):
        script_path = chat_dir / filename
        if script_path.exists() and script_path.is_file():
            return script_path
    return None


def _run_interactive_script(
    script_path: Path,
    input_text: str,
    init_messages: list[dict],
    providers_state: dict,
    event_loop: Any,
    notify_fn: Any,
    retry_on_rate_limit: bool = False,
    delta_fn: Optional[Any] = None,
) -> PromptResult:
    """Execute a DSL script in the current (executor) thread.

    Called from ``execute_prompt_script`` inside a thread-pool executor so
    that blocking sync I/O (MCP HTTP calls, LLM bridge) does not stall the
    event loop.

    Injected globals
    ----------------
    ``input_text`` / ``user_message`` / ``user_query``
        Current user message (str).
    ``Search``
        Context manager — injects retrieval results into ctx before prompt().
    ``MessageHistory``
        Context manager — limits history to last n turn-pairs.
    ``McpServer``
        Context manager — registers MCP tool schemas.
    ``prompt``
        The **only** LLM-calling primitive.
        Signature: ``prompt(text=None, provider="default", **kwargs) -> str``
    ``notify``
        Callable — sends a streaming message to the frontend.
    ``delay``
        ``time.sleep`` alias.
    ``logger``
        Pre-configured ``logging.Logger``.

    ``print()`` output (if any) overrides the last ``prompt()`` return as the
    final response, allowing scripts to return static text without an LLM call.
    """
    from common.tools_dsl import (
        DslRunContext,
        make_mcp_server_class,
        make_message_history_class,
        make_notify_fn,
        make_prompt_fn,
    )

    ctx = DslRunContext(
        messages=list(init_messages),
        providers_state=providers_state,
        event_loop=event_loop,
        notify_fn=notify_fn,
        retry_on_rate_limit=retry_on_rate_limit,
        delta_fn=delta_fn,
    )

    import time as _time

    McpServerClass = make_mcp_server_class(ctx)
    SearchClass = make_search_class(ctx)
    MessageHistoryClass = make_message_history_class(ctx)
    prompt_fn = make_prompt_fn(ctx)
    notify_dsl_fn = make_notify_fn(ctx)
    script_logger = logging.getLogger(f"prompt_dsl.script.{script_path.stem}")

    captured_output = io.StringIO()
    with contextlib.redirect_stdout(captured_output):
        module_globals = runpy.run_path(
            str(script_path),
            init_globals={
                "input_text": input_text,
                "user_message": input_text,
                "user_query": input_text,
                "input": _make_input(input_text),
                "Search": SearchClass,
                "MessageHistory": MessageHistoryClass,
                "McpServer": McpServerClass,
                "prompt": prompt_fn,
                "notify": notify_dsl_fn,
                "delay": _time.sleep,
                "logger": script_logger,
            },
        )

    # print() output takes priority over the last prompt() return value.
    stdout_text = captured_output.getvalue().strip()
    if stdout_text:
        ctx.final_response = stdout_text

    docstring = module_globals.get("__doc__")
    override = module_globals.get("_override")

    return PromptResult(
        system_message=docstring,
        llm_called=ctx.llm_called,
        final_response=ctx.final_response,
        accumulated_messages=ctx.messages,
        full_override=override if isinstance(override, dict) else None,
    )


async def execute_prompt_script(
    script_path: Path,
    input_text: str,
    init_messages: list[dict],
    providers_state: dict,
    notify_fn: Any,
    retry_on_rate_limit: bool = False,
    delta_fn: Optional[Any] = None,
) -> PromptResult:
    """Execute a DSL script asynchronously.

    Runs ``_run_interactive_script`` in a thread-pool executor so blocking
    MCP HTTP calls and sync-to-async LLM bridges do not stall the event loop.

    Parameters
    ----------
    script_path:
        Path to the prompt DSL script.
    input_text:
        Current user message.
    init_messages:
        Pre-built message list (system + history + user turn).
    providers_state:
        Provider state dict for LLM calls.
    notify_fn:
        Thread-safe callable for forwarding notifications to the frontend.
    delta_fn:
        Thread-safe callable for forwarding LLM token deltas to the frontend.
        When set and no tools are active, ``prompt()`` streams tokens through
        this callback instead of returning the full response at once.
    """
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        _run_interactive_script,
        script_path,
        input_text,
        init_messages,
        providers_state,
        loop,
        notify_fn,
        retry_on_rate_limit,
        delta_fn,
    )
    return result
