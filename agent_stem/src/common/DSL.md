# Prompt DSL

The prompt DSL is a lightweight Python-based system for customizing how the
`/v1/agent/chat` endpoint constructs prompts and calls the LLM. Users mount a
`cortex` directory and place a Python script at `cortex/chat/prompt.py` (or
`cortex/chat/agent.py` as a fallback).

---

## How it works

When a chat request arrives the agent runtime:

1. Looks for `cortex/chat/prompt.py`.
2. If found, executes it with `runpy.run_path` inside a captured-stdout
   context.
3. Extracts:
   - **System prompt** — the module-level docstring (`"""..."""`).
   - **User message** — everything that was `print()`-ed (blank lines split
     output into multiple user messages).
   - **Agent config overrides** — any values set on the injected `agent`
     object.
4. Builds the final LLM call from these values.

If no script is found, the default system message from the environment is
used and the raw user input is passed through unchanged.

---

## Injected globals

The following names are available inside `prompt.py` without any import:

| Name              | Type / Value                                   |
|-------------------|------------------------------------------------|
| `input_text`      | `str` — the current user message               |
| `user_message`    | `str` — alias for `input_text`                 |
| `input()`         | `callable` — returns `input_text` (no stdin)   |
| `message_history` | `list[dict]` — mutable conversation history    |
| `agent`           | `AgentConfig` — parameter overrides (see below)|
| `search`          | `Search` — context manager class (see below)   |

---

## System prompt

The module-level docstring becomes the system prompt:

```python
"""You are a helpful assistant."""
```

---

## User message

Everything written with `print()` replaces the raw user input as the message
sent to the LLM. Blank lines between `print()` calls split output into
multiple user message objects (each appended as a separate `role: user`
entry).

```python
"""You are a helpful assistant."""

print(input_text)          # pass through unchanged
```

If the script produces no output, the original user message is used as-is.

---

## `search` — RAG context manager

`search(query, ...)` is a context manager. On `__enter__` it runs a vector
search and prints each result's text to stdout (so it becomes part of the
user message). The results list is also returned for direct use inside the
`with` block.

```python
with search(input()):
    print("User question: " + input())
```

This produces a user message that contains the retrieved text followed by
the user's question, which the LLM can then use to answer.

### Parameters

| Parameter    | Default        | Description                                      |
|--------------|----------------|--------------------------------------------------|
| `query`      | —              | Free-text query sent to the embedding server     |
| `collection` | `None`         | Restrict to one collection; `None` = search all  |
| `top_k`      | `5`            | Maximum number of results                        |
| `filter`     | `None`         | Equality-filter dict (`{"file_path": "..."}`)    |

### Accessing results directly

```python
with search(input(), collection="shelf1", top_k=3) as results:
    for r in results:
        print(r["section_title"], r["score"])
    print("User question: " + input())
```

### Result format

Each result dict contains at minimum:

| Key                    | Description                          |
|------------------------|--------------------------------------|
| `score`                | Relevance score (higher = better)    |
| `collection`           | Collection / table name              |
| `file_path`            | Source PDF path relative to library  |
| `section_title`        | Heading of the chunk                 |
| `text`                 | Chunk text                           |
| `book`                 | Dict with `title`, `tags`, etc.      |
| `chunking_completed_at`| ISO timestamp of last index update   |

---

## `agent` — parameter overrides

The `agent` object lets the script override LLM parameters for this request:

```python
agent.temperature = 0.2
agent.max_tokens = 512
agent.stream = True
agent.stream_format = "ndjson"   # or "sse"
agent.model = "gpt-4o"           # override default provider model
```

| Attribute      | Type              | Description                         |
|----------------|-------------------|-------------------------------------|
| `model`        | `str \| None`     | Override model selection            |
| `temperature`  | `float \| None`   | Sampling temperature                |
| `max_tokens`   | `int \| None`     | Maximum tokens to generate          |
| `stream`       | `bool \| None`    | Enable streaming                    |
| `stream_format`| `str \| None`     | `"sse"` or `"ndjson"`               |
| `tool_choice`  | `str \| None`     | Tool selection preference           |
| `params`       | `dict`            | Free-form LiteLLM parameters        |

---

## `message_history`

A mutable list of `{"role": ..., "content": ...}` dicts. The script may
inspect or modify it. The modified copy is used to build the conversation
context for the LLM call.

```python
# Remove the last assistant message before re-sending
if message_history and message_history[-1]["role"] == "assistant":
    message_history.pop()
```

---

## Examples

### Minimal — system prompt only

```python
"""You are a concise assistant. Always reply in one sentence."""
```

### Pass-through with temperature override

```python
"""You are a creative writing assistant."""

agent.temperature = 0.9
print(input_text)
```

### RAG — answer from documents

```python
"""You are a helpful assistant. Use the search results below to answer
the user's question. If the answer is not in the results, say so."""

with search(input()):
    print("User question: " + input())
```

### RAG — restricted collection

```python
"""You are a rules lawyer for tabletop RPGs."""

with search(input(), collection="shelf1", top_k=3):
    print("Question: " + input())
```

### Structured override (advanced)

```python
"""You are a JSON-only assistant."""

_override = {
    "messages": [
        {"role": "system", "content": "Reply only with valid JSON."},
        {"role": "user", "content": input_text},
    ]
}
```

---

## Implementation

The DSL runtime lives in `agent_stem/src/common/prompt_dsl.py`.

| Symbol                  | Description                                               |
|-------------------------|-----------------------------------------------------------|
| `AgentConfig`           | Dataclass for LLM parameter overrides                     |
| `PromptResult`          | Return type of `execute_prompt_script`                    |
| `Search`                | Context manager class injected as `search`                |
| `find_prompt_script()`  | Locates `prompt.py` / `agent.py` under `cortex/chat/`     |
| `execute_prompt_script()`| Runs a script and returns a `PromptResult`               |
| `load_prompt_dsl()`     | Entry point called by `agent_chat.py` on each request     |

---

# Evaluation DSL

The evaluation DSL follows the same philosophy: place `cortex/chat/eval.py`
next to `prompt.py` to enable the `POST /private/v1/agent/evaluate` API.

The module docstring becomes the suite name. `eval(...)` at module level
configures the run. Every non-underscore function is a test case.

```python
\"\"\"My eval suite.\"\"\"

eval(repeat=2, threshold=1)

def greets_user():
    with question("Hello!"):
        expect(r"(?i)hello|hi")

def remembers_name():
    assume("My name is Alice.")
    with question("What is my name?"):
        expect(r"(?i)\\bAlice\\b")
```

## Injected globals

| Name | Description |
|---|---|
| `eval(...)` | Suite-level config: `repeat`, `threshold`, `model`, `judge_model` |
| `step(text?, image?, audio?, **kwargs)` | Context manager: send a turn, scope expectations |
| `question(...)` | Alias for `step` |
| `response_to(...)` | Alias for `step` |
| `expect(value)` | Attach a check — string → regexp, callable → truthy, `similar_to` → embedding, `judge` → LLM |
| `assume(text)` | Send a turn, discard the response |
| `similar_to(text, threshold)` | Embedding cosine-similarity checker (requires embedding server) |
| `judge(prompt?)` | LLM-as-judge checker; prompt defaults to the case docstring |

## HTTP API

| Method | Path | Description |
|---|---|---|
| `POST` | `/private/v1/agent/evaluate` | Start a run (202) or return 409 if one is already running |
| `GET` | `/private/v1/agent/evaluate` | 202 while running, 200 with results, 404 if no run yet |
| `DELETE` | `/private/v1/agent/evaluate` | Cancel the in-progress run (200) or 404 if none |

## Implementation

The eval DSL runtime lives in `agent_stem/src/common/eval_dsl.py`.

| Symbol | Description |
|---|---|
| `SuiteConfig` | Dataclass for `eval()` configuration |
| `ParsedSuite` | Result of parsing an `eval.py` script |
| `StepContext` | Context manager for `with step():` blocks |
| `find_eval_script()` | Locates `eval.py` under `cortex/chat/` |
| `parse_eval_script()` | Collects cases and config without executing LLM calls |
| `run_eval_suite()` | Entry point called by the POST endpoint handler |
