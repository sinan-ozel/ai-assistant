"""Python-based DSL for customizable prompt generation.

This module provides a runtime for executing user-defined Python scripts
that control prompt construction, model parameters, and conversation behavior.

DSL Contract:
- Module docstring  → system prompt
- print() calls     → user message content (blank lines split into separate messages)
- search(query)     → Search object; use with ``as`` or print() to get results as text
- input()           → returns the current user's message text
- agent object      → model / parameter configuration
- message_history   → mutable conversation list

Minimal example (``cortex/chat/prompt.py``)::

    \"\"\"You are a helpful assistant.\"\"\"

RAG example — context manager::

    \"\"\"You are a helpful assistant. Use the search results below.\"\"\"

    with search(input()) as results:
        print(results)
        print("User question: " + input())

RAG example — direct use::

    \"\"\"You are a helpful assistant. Use the search results below.\"\"\"

    results = Search(input_text)
    print(results)
    print("User question: " + input_text)

RAG example — inline formatting::

    \"\"\"You are a helpful assistant. Use the search results below.\"\"\"

    with Search(input()) as results:
        print("Search results:\\n" + results + "\\n\\nUser question: " + input())
"""

import contextlib
import io
import logging
import runpy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from common.search import DEFAULT_TOP_K, run_search

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration object exposed to DSL scripts via the ``agent`` variable.

    Attributes:
        model: Override the default model selection.
        temperature: Sampling temperature.
        max_tokens: Maximum tokens to generate.
        stream: Enable streaming response.
        stream_format: Streaming format (``"sse"`` or ``"ndjson"``).
        tool_choice: Tool selection preference.
        params: Free-form provider parameters passed through to LiteLLM.
    """

    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: Optional[bool] = None
    stream_format: Optional[str] = None
    tool_choice: Optional[str] = None
    params: dict[str, Any] = field(default_factory=dict)
    _tools: list[str] = field(default_factory=list, repr=False)

    def use_tools(self, *tool_names: str):
        """Enable specific tools for this request."""
        self._tools.extend(tool_names)


@dataclass
class PromptResult:
    """Result of executing a DSL script.

    Attributes:
        system_message: System prompt (from module docstring).
        user_messages: Captured print() output split on blank lines.
        agent_config: Agent configuration set by the script.
        full_override: Structured override dict (set via ``_override``).
        message_history: Conversation history, possibly mutated by the script.
    """

    system_message: Optional[str] = None
    user_messages: list[str] = field(default_factory=list)
    agent_config: AgentConfig = field(default_factory=AgentConfig)
    full_override: Optional[dict] = None
    message_history: Optional[list[dict]] = None


class Search:
    """Vector search helper for DSL scripts.

    Can be used as a context manager or printed directly — both return the
    search results as a formatted string.  The search is run lazily on first
    access and cached so that multiple uses of the same instance do not
    repeat the query.

    Parameters
    ----------
    query:
        Free-text search query sent to the embedding server.
    collection:
        Single collection / table to restrict the search to.  ``None``
        searches all available collections.
    top_k:
        Maximum number of results to return.
    filter:
        Optional equality-filter dict (see ``common.search.run_search``).

    Examples::

        # Context manager — results as a string via ``as``
        with Search(input()) as results:
            print(results)
            print("User question: " + input())

        # Direct use — print() calls __str__
        results = Search(input_text)
        print(results)
        print("User question: " + input_text)

        # Inline formatting
        with Search(input()) as results:
            print("Search results:\\n" + results + "\\n\\nUser question: " + input())
    """

    def __init__(
        self,
        query: str,
        collection: Optional[str] = None,
        top_k: int = DEFAULT_TOP_K,
        filter: Optional[dict] = None,
    ):
        self._query = query
        self._collection = collection
        self._top_k = top_k
        self._filter = filter
        self._cached: Optional[str] = None
        self._used: bool = False

    def _fetch(self) -> str:
        """Run the search and return formatted results as a string.

        Results are cached after the first call so repeated access does not
        re-run the query.
        """
        if self._cached is not None:
            return self._cached

        collections = (
            [self._collection] if self._collection is not None else None
        )
        logger.debug(
            "DSL search: query=%r collection=%r top_k=%d filter=%r",
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
            "DSL search: got %d result(s): %s",
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
        self._used = True
        return self._fetch()

    def __add__(self, other: str) -> str:
        self._used = True
        return self._fetch() + other

    def __radd__(self, other: str) -> str:
        self._used = True
        return other + self._fetch()

    def __enter__(self) -> "Search":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._used:
            print(self._fetch())  # noqa: T201
        return False


def _make_input(input_text: str):
    """Return an ``input()`` override that always returns *input_text*.

    Injected into DSL scripts so ``input()`` yields the current user message
    without reading from stdin.
    """

    def input(_prompt=""):  # noqa: A001
        return input_text

    return input


def find_prompt_script(cortex_path: str) -> Optional[Path]:
    """Return the path to the prompt DSL script, or ``None`` if not found.

    Looks for ``prompt.py`` then ``agent.py`` inside ``<cortex_path>/chat/``.
    """
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


def execute_prompt_script(
    script_path: Path,
    input_text: str,
    message_history: list[dict],
    default_system_message: str,
) -> PromptResult:
    """Execute a prompt DSL script and return a structured result.

    The script is run with ``runpy.run_path`` inside a captured stdout
    context.  The following names are injected as globals:

    ==================  ==================================================
    Name                Value
    ==================  ==================================================
    ``input_text``      Current user message (str)
    ``user_message``    Alias for ``input_text``
    ``input``           Callable that returns ``input_text`` (no stdin)
    ``message_history`` Mutable copy of the conversation history
    ``agent``           :class:`AgentConfig` instance for parameter overrides
    ``search``          :class:`Search` context-manager class
    ``Search``          Alias for ``search`` (capitalised form)
    ``library``         Alias for ``search``
    ``Library``         Alias for ``search``
    ==================  ==================================================

    Parameters
    ----------
    script_path:
        Path to the Python DSL script.
    input_text:
        Current user message.
    message_history:
        Conversation history passed to the script.
    default_system_message:
        Fallback system prompt when the script has no docstring.
    """
    agent_config = AgentConfig()
    script_history = list(message_history)
    captured_output = io.StringIO()

    with contextlib.redirect_stdout(captured_output):
        module_globals = runpy.run_path(
            str(script_path),
            init_globals={
                "input_text": input_text,
                "user_message": input_text,
                "input": _make_input(input_text),
                "message_history": script_history,
                "agent": agent_config,
                "search": Search,
                "Search": Search,
                "library": Search,
                "Library": Search,
            },
        )

    return_value = module_globals.get("__return__") or module_globals.get(
        "_override"
    )
    docstring = module_globals.get("__doc__")
    stdout_content = captured_output.getvalue()

    user_messages = []
    if stdout_content.strip():
        for part in stdout_content.split("\n\n"):
            cleaned = part.strip()
            if cleaned:
                user_messages.append(cleaned)

    return PromptResult(
        system_message=docstring if docstring else default_system_message,
        user_messages=user_messages,
        agent_config=agent_config,
        full_override=return_value if isinstance(return_value, dict) else None,
        message_history=script_history,
    )


def load_prompt_dsl(
    input_text: str,
    message_history: list[dict],
    default_system_message: str,
) -> Optional[PromptResult]:
    """Load and execute the prompt DSL from the cortex folder.

    Looks for ``/app/cortex/chat/prompt.py`` (or ``agent.py``).  Returns
    ``None`` when no script is found.

    Parameters
    ----------
    input_text:
        Current user message.
    message_history:
        Current conversation history.
    default_system_message:
        Fallback system prompt when the script has no docstring.
    """
    cortex_path = "/app/cortex"
    script_path = find_prompt_script(cortex_path)
    if not script_path:
        logger.debug("DSL: no prompt script found in %s.", cortex_path)
        return None

    logger.info("DSL: executing %s.", script_path)
    try:
        result = execute_prompt_script(
            script_path, input_text, message_history, default_system_message
        )
    except Exception as e:
        logger.error(
            "DSL: error executing %s: %s", script_path, e, exc_info=True
        )
        raise

    logger.info(
        "DSL: system_message=%r user_messages=%d.",
        (result.system_message or "")[:80],
        len(result.user_messages),
    )
    return result
