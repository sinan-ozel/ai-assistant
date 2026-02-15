"""
Example usage of the Agent STEM framework.

This demonstrates:
- Setting up short and long-term memory
- Registering tools
- Running agent conversations with identity
"""

from agent_stem.stem import (
    RedisShortTermMemory,
    QdrantLongTermMemory,
    Agent,
    ToolRegistry,
    create_tool,
)


# Example embedding function (stub - replace with real embeddings)
def dummy_embedding(text: str) -> list[float]:
    """Stub embedding function. Replace with OpenAI, sentence-transformers, etc."""
    # In production, use something like:
    # from openai import OpenAI
    # client = OpenAI()
    # response = client.embeddings.create(input=text, model="text-embedding-3-small")
    # return response.data[0].embedding
    return [0.0] * 1536


# Example tools
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


def store_fact(memory, user_id: str, conversation_id: str, text: str) -> str:
    """Store a fact in long-term memory."""
    memory.add(
        user_id=user_id,
        conversation_id=conversation_id,
        item={"text": text},
    )
    return f"Stored fact: {text}"


def main():
    """Run example agent conversations."""

    # Initialize memory backends
    short_memory = RedisShortTermMemory(
        redis_host="redis",
        redis_port=6379,
    )

    long_memory = QdrantLongTermMemory(
        collection="agent_facts",
        embedding_fn=dummy_embedding,
        qdrant_host="qdrant",
        qdrant_port=6333,
    )

    # Register tools
    tool_registry = ToolRegistry()

    tool_registry.register(create_tool(
        name="add_numbers",
        description="Add two integers together",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "integer", "description": "First number"},
                "b": {"type": "integer", "description": "Second number"},
            },
            "required": ["a", "b"],
        },
        function=add_numbers,
    ))

    tool_registry.register(create_tool(
        name="store_fact",
        description="Store an important fact in long-term memory",
        parameters={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The fact to store"},
            },
            "required": ["text"],
        },
        function=store_fact,
    ))

    # Create agent
    agent = Agent(
        short_memory=short_memory,
        long_memory=long_memory,
        tool_registry=tool_registry,
        model="gpt-4o-mini",  # or "openai/gpt-4o-mini" for local routing
    )

    # Example conversation
    user_id = "user-123"
    conversation_id = "conv-001"

    print("=== Agent STEM Example ===\n")

    # First interaction - store a fact
    print("User: Remember that my favorite color is blue.")
    response = agent.step(
        user_id=user_id,
        conversation_id=conversation_id,
        user_input="Remember that my favorite color is blue.",
    )
    print(f"Agent: {response}\n")

    # Second interaction - recall from memory
    print("User: What is my favorite color?")
    response = agent.step(
        user_id=user_id,
        conversation_id=conversation_id,
        user_input="What is my favorite color?",
    )
    print(f"Agent: {response}\n")

    # Third interaction - use tool
    print("User: What is 7 + 15?")
    response = agent.step(
        user_id=user_id,
        conversation_id=conversation_id,
        user_input="What is 7 + 15?",
    )
    print(f"Agent: {response}\n")

    # New conversation, same user
    conversation_id = "conv-002"

    print("=== New Conversation ===\n")
    print("User: Do you remember my favorite color?")
    response = agent.step(
        user_id=user_id,
        conversation_id=conversation_id,
        user_input="Do you remember my favorite color?",
    )
    print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()
