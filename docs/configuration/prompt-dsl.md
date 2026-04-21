# Agent Prompt DSL

Place `cortex/chat/prompt.py` to customise the `POST /v1/agent/chat` endpoint.
The file is executed on every request. It controls the system message and can inject
context into the conversation.

## Minimal example — system message only

The module-level docstring becomes the system message:

```python
# cortex/chat/prompt.py

"""
You are a helpful assistant called "Son of Anton".
You were designed in Silicon Valley and specialize in debugging code.
"""
```

No `print()` needed. If the docstring is the only thing in the file, the user's message
is passed through unchanged.

## Passing the message through

Always end with `print(input_text)` to forward the user's message to the LLM:

```python
"""You are a helpful assistant."""

print(input_text)
```

## Injecting retrieval context (RAG)

Use `Search()` to retrieve relevant chunks from the document library, then print them
before the user's message:

```python
"""
You are a helpful assistant with access to a document library.
Use the retrieved context to answer questions accurately.
"""

results = Search(input_text)
print(results)
print(input_text)
```

`Search()` queries all collections. To restrict to one:

```python
results = Search(input_text, "shelf1")
```

## DSL globals available in `prompt.py`

These names are injected — no imports required:

| Name | Type | Description |
|---|---|---|
| `input_text` | `str` | The user's message for this turn |
| `Search(query, collection=None)` | function | Vector search over the document library |
| `agent` | object | Configuration DSL object (see below) |

## `agent` configuration object

Set agent-level parameters via the `agent` object:

```python
"""You are a helpful assistant."""

agent.temperature = 0.2
agent.max_tokens = 2048

print(input_text)
```

| Attribute | Type | Description |
|---|---|---|
| `agent.temperature` | float | Sampling temperature (0.0–2.0) |
| `agent.max_tokens` | int | Maximum tokens to generate |

Values set here override request-level parameters but are overridden by provider YAML settings.

## Multi-collection search example

```python
"""
You are a city guide assistant. You have access to information about Oldtown and Newtown.
Answer questions using only the facts from the relevant collection.
"""

# Search only the 'oldtown' collection
results = Search(input_text, "oldtown")

if results:
    print("Context from the Oldtown guide:")
    print(results)

print(input_text)
```

## What `prompt.py` cannot do (yet)

- Modify the conversation history
- Make multiple LLM calls (planned for a future release)
- Use `image` or `audio` inputs (planned)

For structured multi-step tasks, use [Workflows](workflows.md) instead.
