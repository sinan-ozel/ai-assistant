"""
Basic tests for the Agent STEM framework.

Tests core functionality without requiring external services.
"""

import pytest
from agent_stem.stem import (
    Memory,
    Agent,
    ToolRegistry,
    create_tool,
    build_prompt,
)


class MockMemory(Memory):
    """In-memory mock for testing without Redis/Qdrant."""

    def __init__(self):
        self.items = []

    def add(self, *, user_id: str, conversation_id: str, item: dict):
        self.items.append({
            "user_id": user_id,
            "conversation_id": conversation_id,
            **item,
        })

    def recent(self, *, user_id: str, conversation_id: str, k: int):
        msgs = [
            i for i in self.items
            if i["user_id"] == user_id
            and i["conversation_id"] == conversation_id
        ]
        return msgs[-k:]

    def retrieve(self, *, user_id: str, query: str, k: int):
        # Simple text matching instead of semantic
        results = [
            i for i in self.items
            if i["user_id"] == user_id
            and "text" in i
            and query.lower() in i["text"].lower()
        ]
        return results[:k]


def test_memory_interface():
    """Test abstract memory interface with mock implementation."""
    mem = MockMemory()

    mem.add(
        user_id="user1",
        conversation_id="conv1",
        item={"role": "user", "content": "Hello"},
    )

    recent = mem.recent(user_id="user1", conversation_id="conv1", k=10)
    assert len(recent) == 1
    assert recent[0]["content"] == "Hello"


def test_memory_isolation():
    """Test that memory isolates users and conversations."""
    mem = MockMemory()

    mem.add(user_id="user1", conversation_id="conv1", item={"text": "A"})
    mem.add(user_id="user1", conversation_id="conv2", item={"text": "B"})
    mem.add(user_id="user2", conversation_id="conv1", item={"text": "C"})

    # User 1, conv 1 should only see A
    recent = mem.recent(user_id="user1", conversation_id="conv1", k=10)
    assert len(recent) == 1
    assert recent[0]["text"] == "A"

    # User 1, conv 2 should only see B
    recent = mem.recent(user_id="user1", conversation_id="conv2", k=10)
    assert len(recent) == 1
    assert recent[0]["text"] == "B"

    # User 2 should only see C
    recent = mem.recent(user_id="user2", conversation_id="conv1", k=10)
    assert len(recent) == 1
    assert recent[0]["text"] == "C"


def test_tool_registry():
    """Test tool registration and execution."""
    registry = ToolRegistry()

    def add(a: int, b: int) -> int:
        return a + b

    tool = create_tool(
        name="add",
        description="Add numbers",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"},
            },
            "required": ["a", "b"],
        },
        function=add,
    )

    registry.register(tool)

    # Test execution
    result = registry.execute("add", {"a": 3, "b": 5})
    assert result == 8

    # Test schemas
    schemas = registry.get_schemas()
    assert len(schemas) == 1
    assert schemas[0]["function"]["name"] == "add"


def test_prompt_builder():
    """Test prompt compilation."""
    system = "You are helpful"
    history = [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello!"},
    ]
    retrieved = [
        {"text": "User likes blue"},
    ]
    user_input = "What's my favorite color?"

    messages = build_prompt(system, history, retrieved, user_input)

    # Should have: system + retrieved context + history + user input
    assert len(messages) >= 5
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == system
    assert "blue" in messages[1]["content"]
    assert messages[-1]["content"] == user_input


def test_tool_with_memory_injection():
    """Test that tools can receive memory via injection."""
    registry = ToolRegistry()

    def store_fact(memory: Memory, user_id: str, conversation_id: str, text: str):
        memory.add(
            user_id=user_id,
            conversation_id=conversation_id,
            item={"text": text},
        )
        return "stored"

    registry.register(create_tool(
        name="store_fact",
        description="Store a fact",
        parameters={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
            },
            "required": ["text"],
        },
        function=store_fact,
    ))

    # Create mock agent
    short_mem = MockMemory()
    long_mem = MockMemory()

    agent = Agent(
        short_memory=short_mem,
        long_memory=long_mem,
        tool_registry=registry,
    )

    # Execute tool with context injection
    result = agent._execute_tool_with_context(
        name="store_fact",
        arguments='{"text": "Sky is blue"}',
        user_id="user1",
        conversation_id="conv1",
    )

    assert result == "stored"
    assert len(long_mem.items) == 1
    assert long_mem.items[0]["text"] == "Sky is blue"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
