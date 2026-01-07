"""
Agent STEM - Simple Transparent Extensible Memory

A minimal agentic framework with:
- Abstract memory interface
- Redis-backed short-term memory
- Qdrant-backed long-term memory
- LiteLLM integration
- Tool execution
- Identity-aware (user_id, conversation_id)
"""

from .memory import Memory
from .short_term_memory import RedisShortTermMemory
from .long_term_memory import QdrantLongTermMemory
from .agent import Agent
from .tools import Tool, ToolRegistry, create_tool
from .prompt import build_prompt

__all__ = [
    "Memory",
    "RedisShortTermMemory",
    "QdrantLongTermMemory",
    "Agent",
    "Tool",
    "ToolRegistry",
    "create_tool",
    "build_prompt",
]
