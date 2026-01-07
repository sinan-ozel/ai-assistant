"""
Tool execution framework for agents.

Provides:
- Tool definition and registration
- JSON Schema for tool parameters
- Type-safe execution
"""

import json
from typing import Dict, Any, Callable, List, Optional
from dataclasses import dataclass


@dataclass
class Tool:
    """
    A tool that can be called by the agent.

    Attributes:
        name: Tool identifier
        description: Human-readable description
        parameters: JSON Schema for parameters
        function: Callable that executes the tool
    """
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable


class ToolRegistry:
    """
    Registry for managing available tools.

    Provides:
    - Tool registration
    - OpenAI-compatible tool schemas
    - Tool execution dispatch
    """

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool in the registry."""
        self.tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)

    def get_schemas(self) -> List[Dict[str, Any]]:
        """
        Get OpenAI-compatible tool schemas for all registered tools.

        Returns:
            List of tool schemas suitable for LiteLLM
        """
        schemas = []
        for tool in self.tools.values():
            schemas.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            })
        return schemas

    def execute(
        self,
        name: str,
        arguments: str | Dict[str, Any],
    ) -> Any:
        """
        Execute a tool by name with given arguments.

        Args:
            name: Tool name
            arguments: JSON string or dict of arguments

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
        """
        tool = self.get(name)
        if tool is None:
            raise ValueError(f"Tool '{name}' not found")

        # Parse arguments if string
        if isinstance(arguments, str):
            args = json.loads(arguments)
        else:
            args = arguments

        # Execute tool
        return tool.function(**args)


def create_tool(
    name: str,
    description: str,
    parameters: Dict[str, Any],
    function: Callable,
) -> Tool:
    """
    Helper function to create a tool.

    Args:
        name: Tool identifier
        description: Human-readable description
        parameters: JSON Schema for parameters
        function: Callable that executes the tool

    Returns:
        Configured Tool instance
    """
    return Tool(
        name=name,
        description=description,
        parameters=parameters,
        function=function,
    )
