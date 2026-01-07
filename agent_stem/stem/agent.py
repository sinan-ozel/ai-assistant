"""
Main agent implementation.

A stateless agent that:
- Manages identity (user_id, conversation_id)
- Orchestrates memory (short + long term)
- Calls LLM via LiteLLM
- Executes tools
- Maintains conversation state
"""

from typing import Any, Optional
from litellm import completion

from .memory import Memory
from .tools import ToolRegistry
from .prompt import build_prompt


class Agent:
    """
    Stateless agent with identity-aware memory and tool execution.

    The agent coordinates:
    - Short-term memory (conversation history)
    - Long-term memory (semantic facts/context)
    - LLM inference via LiteLLM
    - Tool execution

    All state lives in memory backends, not in the agent instance.
    """

    def __init__(
        self,
        short_memory: Memory,
        long_memory: Memory,
        tool_registry: ToolRegistry,
        model: str = "gpt-4o-mini",
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize the agent.

        Args:
            short_memory: Short-term memory implementation
            long_memory: Long-term memory implementation
            tool_registry: Registry of available tools
            model: LiteLLM model identifier
            system_prompt: System instruction for the agent
        """
        self.short_memory = short_memory
        self.long_memory = long_memory
        self.tool_registry = tool_registry
        self.model = model

        self.system_prompt = system_prompt or (
            "You are a helpful assistant. "
            "Use tools when appropriate. "
            "Store important facts in memory for future reference."
        )

    def step(
        self,
        *,
        user_id: str,
        conversation_id: str,
        user_input: str,
        retrieve_context: bool = True,
        max_history: int = 6,
        max_context: int = 3,
    ) -> str:
        """
        Execute one agent step.

        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            user_input: User's message
            retrieve_context: Whether to retrieve from long-term memory
            max_history: Max conversation history to include
            max_context: Max retrieved context items

        Returns:
            Agent's response text
        """
        # Retrieve context from long-term memory
        retrieved = []
        if retrieve_context:
            retrieved = self.long_memory.retrieve(
                user_id=user_id,
                query=user_input,
                k=max_context,
            )

        # Get recent conversation history
        history = self.short_memory.recent(
            user_id=user_id,
            conversation_id=conversation_id,
            k=max_history,
        )

        # Build prompt
        messages = build_prompt(
            self.system_prompt,
            history,
            retrieved,
            user_input,
        )

        # Get tool schemas
        tools = self.tool_registry.get_schemas()

        # Call LLM
        response = completion(
            model=self.model,
            messages=messages,
            tools=tools if tools else None,
            tool_choice="auto" if tools else None,
        )

        msg = response.choices[0].message

        # Handle tool calls
        if msg.tool_calls:
            tool_results = []

            for call in msg.tool_calls:
                name = call.function.name
                args = call.function.arguments

                try:
                    # Inject memory and identity for tools that need it
                    result = self._execute_tool_with_context(
                        name=name,
                        arguments=args,
                        user_id=user_id,
                        conversation_id=conversation_id,
                    )
                    tool_results.append(str(result))

                    # Store tool call and result in short-term memory
                    self.short_memory.add(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        item={
                            "role": "assistant",
                            "content": f"[Called tool: {name}]",
                        },
                    )
                    self.short_memory.add(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        item={
                            "role": "tool",
                            "content": str(result),
                        },
                    )

                except Exception as e:
                    error_msg = f"Tool execution failed: {str(e)}"
                    tool_results.append(error_msg)

                    self.short_memory.add(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        item={
                            "role": "tool",
                            "content": error_msg,
                        },
                    )

            # Return tool results summary
            return "\n".join(tool_results)

        # No tool calls - regular response
        else:
            response_text = msg.content

            # Store assistant response in short-term memory
            self.short_memory.add(
                user_id=user_id,
                conversation_id=conversation_id,
                item={
                    "role": "assistant",
                    "content": response_text,
                },
            )

            return response_text

    def _execute_tool_with_context(
        self,
        name: str,
        arguments: str,
        user_id: str,
        conversation_id: str,
    ) -> Any:
        """
        Execute a tool with identity context injection.

        Some tools need access to memory or identity. This method
        handles injecting those dependencies transparently.
        """
        import json

        # Parse arguments
        args = json.loads(arguments) if isinstance(arguments, str) else arguments

        # Check if tool needs memory/identity injection
        tool = self.tool_registry.get(name)
        if tool is None:
            raise ValueError(f"Tool '{name}' not found")

        # Inspect function signature to see what to inject
        import inspect
        sig = inspect.signature(tool.function)

        # Inject dependencies if needed
        if "memory" in sig.parameters:
            args["memory"] = self.long_memory
        if "user_id" in sig.parameters:
            args["user_id"] = user_id
        if "conversation_id" in sig.parameters:
            args["conversation_id"] = conversation_id

        # Execute
        return self.tool_registry.execute(name, args)
