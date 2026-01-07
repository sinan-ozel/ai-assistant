# Agent STEM

**Simple Transparent Extensible Memory** - A minimal agentic framework.

## Architecture

```
┌─────────────┐
│ User Input  │
└──────┬──────┘
       ↓
┌─────────────┐
│ Short-Term  │  (Redis - conversation window)
│   Memory    │
└──────┬──────┘
       ↓
┌─────────────┐
│ Retrieval   │  (Qdrant RAG, semantic)
└──────┬──────┘
       ↓
┌─────────────┐
│ Prompt      │  (system + memory + context)
│ Compiler    │
└──────┬──────┘
       ↓
┌─────────────┐
│ LiteLLM     │
│ (tool call) │
└──────┬──────┘
       ↓
┌─────────────┐
│ Tool Exec   │
└──────┬──────┘
       ↓
┌─────────────┐
│ Memory      │  (write-back)
└─────────────┘
```

## Features

- **Abstract Memory Interface**: Swap implementations without changing agent code
- **Redis Short-Term Memory**: Multiprocessing-safe conversation history using [redis-memory](https://pypi.org/project/redis-memory/)
- **Qdrant Long-Term Memory**: Semantic retrieval with vector embeddings
- **LiteLLM Integration**: Model-agnostic LLM interface
- **Identity-Aware**: First-class support for `user_id` and `conversation_id`
- **Tool Execution**: Type-safe tool calling with automatic context injection
- **Stateless Agent**: All state lives in memory backends

## Core Concepts

### Identity

Every interaction requires:
- `user_id`: Stable user identifier (cross-conversation)
- `conversation_id`: Ephemeral session/thread identifier

This enables:
- Multi-user isolation
- Multiple conversations per user
- Cross-conversation memory retrieval
- No prompt leakage between users

### Memory Types

**Short-Term Memory (Redis)**
- Stores conversation history
- Retrieval is conversation-scoped
- Recent messages in chronological order
- Backed by redis-memory for multiprocess safety

**Long-Term Memory (Qdrant)**
- Stores facts, observations, context
- Retrieval is user-scoped, cross-conversation
- Semantic search via vector embeddings
- Metadata filtering by user_id

### Tools

Tools can:
- Access memory (automatically injected)
- Receive identity context (`user_id`, `conversation_id`)
- Return structured results
- Use JSON Schema for validation

## Usage

See [example.py](example.py) for a complete working example.

```python
from agent_stem.stem import (
    RedisShortTermMemory,
    QdrantLongTermMemory,
    Agent,
    ToolRegistry,
    create_tool,
)

# Initialize memory
short_memory = RedisShortTermMemory()
long_memory = QdrantLongTermMemory(
    collection="facts",
    embedding_fn=your_embedding_function,
)

# Register tools
tools = ToolRegistry()
tools.register(create_tool(
    name="add_numbers",
    description="Add two integers",
    parameters={
        "type": "object",
        "properties": {
            "a": {"type": "integer"},
            "b": {"type": "integer"},
        },
        "required": ["a", "b"],
    },
    function=lambda a, b: a + b,
))

# Create agent
agent = Agent(
    short_memory=short_memory,
    long_memory=long_memory,
    tool_registry=tools,
)

# Run conversation
response = agent.step(
    user_id="user-123",
    conversation_id="conv-001",
    user_input="What is 3 + 5?",
)
```

## Design Principles

1. **Explicit is better than implicit**: Identity flows through every call
2. **Stateless agents**: All state lives in memory backends
3. **Abstract interfaces**: Swap implementations without code changes
4. **Minimal framework**: No hidden magic, no complex abstractions
5. **Debuggable**: Clear data flow, explicit boundaries

## What This Gives You

- ✅ Explicit agent loop
- ✅ Clear memory boundaries
- ✅ Swappable LLM backend
- ✅ Swappable memory stores
- ✅ Deterministic tool execution
- ✅ Debuggable prompt construction
- ✅ Multi-user support
- ✅ Horizontal scaling

## What's Intentionally Omitted

These are *incremental* additions, not architectural changes:

- Memory summarization
- Token budgeting
- Retry/error handling
- Advanced tool orchestration
- Retrieval gating
- Streaming responses
- Multi-agent coordination

## Requirements

- Python 3.12+
- Redis server
- Qdrant server
- LiteLLM-compatible model provider

## Dependencies

```
redis-memory>=0.3.2
qdrant-client
litellm
```

## License

MIT
