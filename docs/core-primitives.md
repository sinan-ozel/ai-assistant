# Core Primitives

Reference for every name injected into `cortex/chat/prompt.py`.  No imports
are needed — all primitives listed here are available as globals at runtime.

---

## Two interfaces

All data in the DSL is a plain `str`.  There are exactly two interfaces:

| Interface    | Direction | Description |
|--------------|-----------|-------------|
| **Prompt**   | → LLM     | A string passed into the LLM as a user message |
| **Response** | ← LLM     | A string returned from the LLM |

`llm()` / `prompt()` is the **only** primitive that calls an LLM.  Every other
primitive builds context or delivers output.

---

## prompt.py primitives

### `input_text` / `user_message`

The current user message, available as two variable names:

| Name           | Type  | Description            |
|----------------|-------|------------------------|
| `input_text`   | `str` | Raw user message       |
| `user_message` | `str` | Alias for `input_text` |

```python
print(input_text)
print(user_message)   # identical
```

---

### `message_history`

```python
message_history: list[dict]
```

Mutable list of `{"role": ..., "content": ...}` dicts representing the
conversation so far, **not** including the current user turn. Changes made
inside the script are used when building the LLM call.

```python
# Drop the last assistant turn before re-sending
if message_history and message_history[-1]["role"] == "assistant":
    message_history.pop()
```

> In interactive mode (`llm()` is present), `message_history` is always
> empty — the pre-built message list is held internally in the run context
> and is not exposed directly.

---

### `agent`

Parameter overrides for the implicit LLM call (non-interactive mode only).
Values set here are applied to the single LLM call that the runtime makes
after the script finishes.

| Attribute       | Type           | Description                                      |
|-----------------|----------------|--------------------------------------------------|
| `model`         | `str \| None`  | Override model selection                         |
| `temperature`   | `float \| None`| Sampling temperature                             |
| `max_tokens`    | `int \| None`  | Maximum tokens to generate                       |
| `stream`        | `bool \| None` | Enable streaming                                 |
| `stream_format` | `str \| None`  | `"sse"` or `"ndjson"`                            |
| `tool_choice`   | `str \| None`  | Tool selection preference                        |
| `params`        | `dict`         | Free-form extra kwargs forwarded to LiteLLM      |

```python
agent.temperature = 0.9
agent.max_tokens = 512
```

---

### `search(query, collection=None, top_k=5, filter=None)`

Vector search context manager. Fetches the closest chunks from the document
library and makes them available inside the `with` block. When the block
exits, any results not already consumed are `print()`-ed automatically (so
they become part of the user message sent to the LLM).

| Parameter    | Default | Description                                           |
|--------------|---------|-------------------------------------------------------|
| `query`      | —       | Free-text query sent to the embedding server          |
| `collection` | `None`  | Restrict to one shelf; `None` searches all            |
| `top_k`      | `5`     | Maximum number of results                             |
| `filter`     | `None`  | Equality-filter dict, e.g. `{"file_path": "foo.pdf"}` |

**Result dict keys**

| Key                    | Description                          |
|------------------------|--------------------------------------|
| `score`                | Relevance score (higher = better)    |
| `collection`           | Collection name                      |
| `file_path`            | Source path relative to library root |
| `section_title`        | Heading of the chunk                 |
| `text`                 | Chunk text                           |
| `book`                 | Dict with `title`, `tags`, etc.      |
| `chunking_completed_at`| ISO timestamp of last index update   |

```python
# Implicit print — results appear before the user question
with search(input_text):
    print("User question: " + input_text)

# Explicit string access
with search(input_text, collection="shelf1", top_k=3) as results:
    print("Search results:\n" + results)
    print("User question: " + input_text)

# Direct string conversion (interactive mode)
chunks = str(Search(input_text))
```

---

## Interactive mode

When `prompt.py` contains any of the names `llm`, `prompt`, `notify`,
`McpServer`, or `mcp`, the runtime switches to **interactive mode**. The
script drives every LLM call explicitly.

---

### `llm(input_text=None, provider="default", temperature=None)` / `prompt(...)`

**The only primitive that calls an LLM.**  `prompt` is an alias for `llm`.

Returns the assistant reply as a plain `str`.  May be called any number of
times in one request.

| Parameter     | Default     | Description                                                          |
|---------------|-------------|----------------------------------------------------------------------|
| `input_text`  | `None`      | If given, used as the user message for this call only — not persisted to message history |
| `provider`    | `"default"` | Provider name; `"default"` selects the configured default provider   |
| `temperature` | `None`      | Overrides the provider YAML's `temperature` for this call only       |

Provider YAML fields (`temperature`, `max_tokens`, `top_p`, `stop`,
`timeout`) are applied as defaults. An explicit kwarg to `llm()` overrides
the YAML value for that single call only.

**Tool dispatch**: when `McpServer` tools are registered, `llm()` offers them
to the LLM automatically.  If the LLM requests tool calls, `llm()` dispatches
them non-blocking and appends the assistant tool-call message to the transient
context so `tools.wait()` can match results.  Plain text responses do not
mutate the message context.

```python
# Basic — uses default provider and its configured temperature
response = llm()

# Append a message for this call only
response = llm("Summarise the above in one sentence.")

# Select a named provider
response = llm(provider="creative")

# Override temperature (e.g. derived from a classifier score)
response = llm(input_text, temperature=0.9)
```

---

### `notify(text)`

Send text to the frontend immediately, without adding it to the LLM message
context.

- **Streaming on**: each call emits one complete chunk to the SSE / NDJSON
  stream with `"notify": true` in the payload.  The Streamlit UI shows all
  but the final `notify()` call in a collapsible **🤔** box and
  displays the last call as the assistant reply.
- **Streaming off**: all calls are collected; only the last one is used as the
  final response.

```python
notify("Thinking…")
response = llm()
notify(response)
```

---

### `delay(seconds)`

Pause execution for `seconds` before the next operation. Useful for pacing
calls when a provider rate-limits on tokens-per-minute. Accepts fractional
values (`delay(0.5)`).

```python
with McpServer("http://tool-server:8000") as tools:
    llm()
    tools.wait()
    delay(3)
    response = llm()
notify(response)
```

---

### `McpServer(url)` / `mcp(url)`

Context manager that **connects to an MCP tool server and registers its
schemas** — it does not call the LLM.

On `__enter__`, tool schemas are added to the shared context so every
subsequent `llm()` call offers them to the LLM automatically.

On `__exit__`, schemas are removed and `wait()` is called automatically.

| Method   | Description                                                          |
|----------|----------------------------------------------------------------------|
| `wait()` | Block until dispatched tool calls complete; append results to context |

`mcp` is an alias for `McpServer`.

```python
# Single-phase
with McpServer("http://tool-server:8000") as tools:
    llm()            # LLM sees schemas; selects and dispatches
    tools.wait()
    response = llm() # LLM sees tool results; gives final answer
notify(response)

# Multi-phase
with McpServer("http://tool-server:8000") as tools:
    notify("Consulting sources…")
    llm()
    tools.wait()
    response = llm()
    notify(response)

    notify("Going deeper…")
    llm()
    tools.wait()
    response = llm()
notify(response)
```

**Timeouts**: every `llm()` call inside interactive mode is wrapped with a
100-second ceiling. MCP HTTP calls have an independent 30-second timeout.

---

## Message history

The persistent conversation history (Redis) is mutated **exactly twice** per
request — the user message is appended before the script runs and the final
response is appended after.  Nothing inside the script changes the persistent
history.

The transient context (`ctx.messages`) grows only when tool calls happen.
See [message-history.md](message-history.md) for the full lifecycle diagram.

---

## eval.py primitives

Place `cortex/chat/eval.py` next to `prompt.py` to enable
`POST /private/v1/agent/evaluate`. The module docstring becomes the suite
name. Every module-level function whose name does not start with `_` is
collected as a test case, in definition order.

---

### `eval(repeat=1, threshold=1, model=None, judge_model=None)`

Suite-level configuration. Call once at module level.

| Parameter     | Default | Description                                           |
|---------------|---------|-------------------------------------------------------|
| `repeat`      | `1`     | How many times to run each case                       |
| `threshold`   | `1`     | Minimum passing runs needed to mark a case as passed  |
| `model`       | `None`  | Override the agent model for the whole suite          |
| `judge_model` | `None`  | Model used for `judge()` calls; defaults to agent model|

```python
eval(repeat=3, threshold=2)
```

---

### `step(text=None, image=None, audio=None, **kwargs)` / `question()` / `response_to()`

Context manager that sends one turn to the agent. All three names are
identical. Subsequent steps continue the same conversation, so multi-turn
memory is tested naturally.

```python
with step("What is the capital of France?"):
    expect("Paris")
```

---

### `assume(text)`

Send a turn to the agent and discard the response. Use it to establish
conversation context before the evaluated steps.

```python
assume("My name is Alice.")
with question("What is my name?"):
    expect("Alice")
```

---

### `expect(value)`

Attach a check to the enclosing `step`. Three check types:

**String → regexp match**

```python
expect("Paris")
expect(r"\b\d{3}\b")
```

**Callable → call with response text, pass if truthy**

```python
expect(lambda r: len(r) > 20)
```

**`similar_to` or `judge` object**

```python
expect(similar_to("a polite refusal", 0.82))
expect(judge("Did the agent correctly identify the calorie count?"))
```

---

### `similar_to(text, threshold)`

Embedding cosine-similarity checker. Passes if the similarity between the
response and `text` is ≥ `threshold`. Requires the embedding server.

---

### `judge(prompt=None)`

LLM-as-judge checker. Passes if the verdict is affirmative. If called with
no argument, the prompt defaults to the case function's docstring.

---

## Eval HTTP API

| Method   | Path                          | Description                                            |
|----------|-------------------------------|--------------------------------------------------------|
| `POST`   | `/private/v1/agent/evaluate`  | Start a run (202) or 409 if one is already running     |
| `GET`    | `/private/v1/agent/evaluate`  | 202 while running, 200 with results, 404 if no run yet |
| `DELETE` | `/private/v1/agent/evaluate`  | Cancel the in-progress run (200) or 404 if none        |

```bash
# Start
curl -X POST http://localhost:8000/private/v1/agent/evaluate

# Run a single case
curl -X POST http://localhost:8000/private/v1/agent/evaluate \
  -H "Content-Type: application/json" \
  -d '{"case": "calories_label"}'

# Poll
curl http://localhost:8000/private/v1/agent/evaluate

# Cancel
curl -X DELETE http://localhost:8000/private/v1/agent/evaluate
```
