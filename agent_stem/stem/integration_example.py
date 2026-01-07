"""
Integration example: Using Agent STEM with the FastAPI endpoints.

This shows how to wire up the agent framework with the existing
/v1/chat/completions and /v1/api/generate endpoints.
"""

from typing import Dict, Any
from agent_stem.stem import (
    RedisShortTermMemory,
    QdrantLongTermMemory,
    Agent,
    ToolRegistry,
    create_tool,
)


def create_agent_for_user(
    user_id: str,
    providers_state: Dict[str, Any],
) -> Agent:
    """
    Factory function to create an agent instance for a user.

    This can be called from FastAPI endpoints to get a configured agent.

    Args:
        user_id: User identifier (from auth/session)
        providers_state: Available LLM providers

    Returns:
        Configured Agent instance
    """
    # Initialize memory backends
    short_memory = RedisShortTermMemory(
        redis_host="redis",
        redis_port=6379,
    )

    # Use a real embedding function in production
    # Example with OpenAI:
    # from openai import OpenAI
    # client = OpenAI()
    # def embed(text):
    #     response = client.embeddings.create(
    #         input=text,
    #         model="text-embedding-3-small"
    #     )
    #     return response.data[0].embedding

    def stub_embedding(text: str):
        # Stub for now - replace with real embeddings
        return [0.0] * 1536

    long_memory = QdrantLongTermMemory(
        collection=f"user_{user_id}_memory",
        embedding_fn=stub_embedding,
        qdrant_host="qdrant",
        qdrant_port=6333,
    )

    # Create tool registry
    tools = ToolRegistry()

    # Register tools
    tools.register(create_tool(
        name="store_fact",
        description="Store an important fact in long-term memory for future reference",
        parameters={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The fact to store"
                },
            },
            "required": ["text"],
        },
        function=lambda memory, user_id, conversation_id, text: (
            memory.add(
                user_id=user_id,
                conversation_id=conversation_id,
                item={"text": text}
            ),
            f"Stored: {text}"
        )[1],
    ))

    # Determine best model from providers_state
    model = "gpt-4o-mini"  # Default
    if providers_state and "providers" in providers_state:
        providers = providers_state["providers"]
        if providers:
            # Use first available provider
            first_provider = next(iter(providers.values()))
            if "model" in first_provider:
                model = first_provider["model"]

    # Create agent
    agent = Agent(
        short_memory=short_memory,
        long_memory=long_memory,
        tool_registry=tools,
        model=model,
        system_prompt=(
            "You are a helpful AI assistant. "
            "You have access to long-term memory across conversations. "
            "When users tell you important information, use the store_fact tool "
            "to remember it for future conversations. "
            "When answering questions, relevant context from past conversations "
            "will be provided to you automatically."
        ),
    )

    return agent


# Example FastAPI endpoint integration:
#
# async def handler(request: dict, providers_state: dict):
#     """
#     Chat completions endpoint with agent integration.
#     """
#     # Extract identity from request (from auth/session)
#     user_id = request.get("user_id", "anonymous")
#     conversation_id = request.get("conversation_id", "default")
#
#     # Get user's message
#     messages = request.get("messages", [])
#     if not messages:
#         raise HTTPException(status_code=400, detail="No messages provided")
#
#     last_message = messages[-1]
#     user_input = last_message.get("content", "")
#
#     # Create agent
#     agent = create_agent_for_user(user_id, providers_state)
#
#     # Run agent step
#     response_text = agent.step(
#         user_id=user_id,
#         conversation_id=conversation_id,
#         user_input=user_input,
#     )
#
#     # Return OpenAI-compatible response
#     return {
#         "id": f"chatcmpl-{uuid.uuid4()}",
#         "object": "chat.completion",
#         "created": int(time.time()),
#         "model": request.get("model", "gpt-4o-mini"),
#         "choices": [{
#             "index": 0,
#             "message": {
#                 "role": "assistant",
#                 "content": response_text,
#             },
#             "finish_reason": "stop",
#         }],
#     }


def example_conversation():
    """
    Example multi-turn conversation with memory.
    """
    import time

    user_id = "user-456"
    conversation_1 = "conv-morning"
    conversation_2 = "conv-afternoon"

    # Assume providers_state is available
    providers_state = {"providers": {}}

    # Create agent
    agent = create_agent_for_user(user_id, providers_state)

    print("=== Conversation 1 (Morning) ===\n")

    # User shares information
    response = agent.step(
        user_id=user_id,
        conversation_id=conversation_1,
        user_input="My name is Alice and I'm learning Python.",
    )
    print(f"User: My name is Alice and I'm learning Python.")
    print(f"Agent: {response}\n")

    # User asks for help
    response = agent.step(
        user_id=user_id,
        conversation_id=conversation_1,
        user_input="Can you recommend a Python project for beginners?",
    )
    print(f"User: Can you recommend a Python project for beginners?")
    print(f"Agent: {response}\n")

    print("\n=== Conversation 2 (Afternoon) ===\n")

    # New conversation - agent should still remember Alice's name
    response = agent.step(
        user_id=user_id,
        conversation_id=conversation_2,
        user_input="What was my name again?",
    )
    print(f"User: What was my name again?")
    print(f"Agent: {response}\n")

    # Should also remember context about learning Python
    response = agent.step(
        user_id=user_id,
        conversation_id=conversation_2,
        user_input="What am I learning?",
    )
    print(f"User: What am I learning?")
    print(f"Agent: {response}\n")


if __name__ == "__main__":
    print(__doc__)
    print("\n" + "="*60 + "\n")

    # Note: This requires Redis and Qdrant to be running
    # And LiteLLM to be configured with API keys

    try:
        example_conversation()
    except Exception as e:
        print(f"Error running example: {e}")
        print("\nNote: Make sure Redis and Qdrant are running,")
        print("and LiteLLM is configured with appropriate API keys.")
