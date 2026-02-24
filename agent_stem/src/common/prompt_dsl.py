"""Python-based DSL for customizable prompt generation.

This module provides a runtime for executing user-defined Python scripts
that control prompt construction, model parameters, and conversation behavior.

DSL Contract:
- Module docstring → system prompt
- print() statements → user message(s)
- agent object → model/parameter configuration
- message_history → mutable conversation list
- return dict → structured override (optional)

Example:
    ```python
    # prompt.py
    \"\"\"
    You are a helpful assistant.
    \"\"\"

    agent.temperature = 0.7
    print(input_text)
    ```
"""

import io
import logging
import runpy
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration object exposed to DSL scripts via 'agent' variable.

    Attributes:
        model: Override model selection
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        stream: Enable streaming response
        stream_format: Streaming format ("sse" or "ndjson")
        tool_choice: Tool selection preference
        params: Free-form provider parameters
        tools: List of enabled tools
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
        system_message: System prompt (from docstring or override)
        user_messages: List of user message contents
        agent_config: Agent configuration
        full_override: Complete structured override (if returned)
        message_history: Modified conversation history
    """

    system_message: Optional[str] = None
    user_messages: list[str] = field(default_factory=list)
    agent_config: AgentConfig = field(default_factory=AgentConfig)
    full_override: Optional[dict] = None
    message_history: Optional[list[dict]] = None


def find_prompt_script(cortex_path: str) -> Optional[Path]:
    """Find the prompt DSL script in the cortex directory.

    Looks for files in order: prompt.py, agent.py

    Args:
        cortex_path: Path to cortex directory (from env CORTEX_FOLDER)

    Returns:
        Path to script file, or None if not found
    """
    if not cortex_path:
        return None

    cortex = Path(cortex_path) / "chat"
    if not cortex.exists() or not cortex.is_dir():
        return None

    # Try multiple filenames
    for filename in ["prompt.py", "agent.py"]:
        script_path = cortex / filename
        if script_path.exists() and script_path.is_file():
            return script_path

    return None


def execute_prompt_script(
    script_path: Path,
    input_text: str,
    message_history: list[dict],
    default_system_message: str,
) -> PromptResult:
    """Execute a prompt DSL script and return structured result.

    Args:
        script_path: Path to the Python DSL script
        input_text: User's input message
        message_history: Current conversation history (mutable)
        default_system_message: Fallback system message

    Returns:
        PromptResult with extracted system/user messages and config
    """
    # Create agent config object
    agent_config = AgentConfig()

    # Make a mutable copy of history for the script
    script_history = list(message_history)

    # Capture stdout
    old_stdout = sys.stdout
    captured_output = io.StringIO()

    try:
        sys.stdout = captured_output

        # Execute script with injected globals
        module_globals = runpy.run_path(
            str(script_path),
            init_globals={
                "input_text": input_text,
                "user_message": input_text,
                "message_history": script_history,
                "agent": agent_config,
            },
        )
        # TODO: Add image_url

        # Check for return dict (full override)
        return_value = module_globals.get("__return__")
        if return_value is None:
            # Check if script explicitly returned something
            # (runpy doesn't capture return values, so we use a sentinel)
            # For now, users can set a global variable for override
            return_value = module_globals.get("_override")

        # Extract docstring as system message (from module __doc__)
        docstring = module_globals.get("__doc__")

        # Get captured stdout
        stdout_content = captured_output.getvalue()

        # Parse stdout into user messages
        # Rule: blank line splits messages
        user_messages = []
        if stdout_content.strip():
            # Split on double newline (blank line)
            parts = stdout_content.split("\n\n")
            for part in parts:
                cleaned = part.strip()
                if cleaned:
                    user_messages.append(cleaned)

        # Build result
        result = PromptResult(
            system_message=docstring if docstring else default_system_message,
            user_messages=user_messages,
            agent_config=agent_config,
            full_override=(
                return_value if isinstance(return_value, dict) else None
            ),
            message_history=script_history,
        )

        return result

    finally:
        sys.stdout = old_stdout


def load_prompt_dsl(
    input_text: str,
    message_history: list[dict],
    default_system_message: str,
) -> Optional[PromptResult]:
    """Load and execute prompt DSL from CORTEX_FOLDER env if available.

    Args:
        input_text: User's input message
        message_history: Current conversation history
        default_system_message: Fallback system message

    Returns:
        PromptResult if DSL script found and executed, None otherwise
    """
    # Check for cortex folder from environment, default to /app/cortex
    cortex_path = "/app/cortex"
    logger.info(f"DSL: Looking for cortex at: {cortex_path}")
    if not cortex_path:
        return None

    # Find prompt script
    script_path = find_prompt_script(cortex_path)
    if not script_path:
        logger.info(f"DSL: No prompt script found in {cortex_path}")
        return None

    logger.info(f"DSL: Found prompt script at: {script_path}")

    # Execute and return result
    try:
        result = execute_prompt_script(
            script_path,
            input_text,
            message_history,
            default_system_message,
        )
        system_msg_preview = (
            result.system_message[:100] if result.system_message else None
        )
        logger.info(
            f"DSL: Execution result - system_message: "
            f"{system_msg_preview}..."
        )
        logger.info(
            f"DSL: Execution result - user_messages count: "
            f"{len(result.user_messages)}"
        )
        return result
    except Exception as e:
        logger.error(f"[PROMPT_DSL] ERROR: {e}", exc_info=True)
        logger.error(
            f"Error executing prompt DSL script {script_path}: {e}",
            exc_info=True,
        )
        raise
