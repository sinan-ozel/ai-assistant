# Prompt DSL

The prompt DSL is a lightweight Python-based system for customizing how the
`/v1/agent/chat` endpoint constructs prompts and calls the LLM. Users mount a
`cortex` directory and place a Python script at `cortex/chat/prompt.py` (or
`cortex/chat/agent.py` as a fallback).

All responses are streamed. There is one execution model — no
interactive/non-interactive split.

---

## How it works

When a chat request arrives the agent runtime:

1. Locates `cortex/chat/prompt.py`.
2. Executes it with `runpy.run_path` in a captured context.
3. Extracts the **system prompt** from the module-level docstring.
4. The final response is:
   - the text passed to `print()`, if called; or
   - the return value of the last `prompt()` call.
5. Streams the response to the client and appends it to persistent
   conversation history (Redis).

The persistent history is updated **exactly twice** per request: the user
message is appended before the script runs, and the final assistant response
is appended after. Nothing inside the script changes the persistent history.

**Every script must call `prompt()` or `print()`.** If neither is called, the
response is empty — this is a script error, not a fallback.

If no script is found, the default system message is used and `prompt()` is
called with the raw user input.

---

## Injected globals

The following names are available inside `prompt.py` without any import:

| Name              | Type / Value                                                      |
|-------------------|-------------------------------------------------------------------|
| `input_text`      | `str` — the current user message                                  |
| `user_message`    | `str` — alias for `input_text`                                    |
| `user_query`      | `str` — alias for `input_text`                                    |
| `Search`          | Context manager — injects retrieval results (see below)           |
| `MessageHistory`  | Context manager — limits conversation history (see below)         |
| `McpServer`       | Context manager — registers MCP tools (see below)                 |
| `delay`           | `time.sleep` alias                                                |
| `logger`          | `logging.Logger` — pre-configured, named `prompt_dsl.script.<stem>` |

---

## System prompt

The module-level docstring becomes the system prompt:

```python
"""You are a helpful assistant."""
```

---

## `prompt(text=input_text, provider="default", **kwargs)`

**The only function that calls an LLM.** Streams the response to the client
and returns the complete reply as a `str`.

The return value of the last `prompt()` call becomes the final response saved
to conversation history, unless overridden by `print()`.

| Parameter  | Default      | Description                                                    |
|------------|--------------|----------------------------------------------------------------|
| `text`     | `input_text` | User message for this call; defaults to the current user input |
| `provider` | `"default"`  | Named provider from provider YAML                              |
| `**kwargs` | —            | Any LiteLLM parameter; overrides provider YAML for this call  |

```python
# Calls LLM with the user's message
response = prompt()

# Custom message
response = prompt("Summarise the above in one sentence.")

# Provider override
response = prompt(provider="creative")

# LiteLLM parameter override
response = prompt(temperature=0.9)
```

---

## `print(text)`

Send `text` directly to the user as the final response, bypassing the LLM.
Saved to conversation history. Whatever is passed is returned verbatim —
`print(input_text)` echoes the user's message; `print("Hello world")` always
returns `"Hello world"` regardless of what the user said.

```python
# Static response — always says this, no matter what the user sends
print("This agent is currently offline.")

# Echo the user's message back
print(input_text)
```

---

## `notify(text)`

Send `text` to the user as an intermediate streaming message. Not saved to
conversation history. Use this for progress updates during long-running
operations.

```python
notify("Searching documents…")
with Search(input_text):
    response = prompt()
```

---

## `with Search(query, collection=None, top_k=5, filter=None)`

Injects retrieval results into the LLM context for all `prompt()` calls inside
the block. On exit the injected results are removed from context.

| Parameter    | Default  | Description                                       |
|--------------|----------|---------------------------------------------------|
| `query`      | —        | Free-text query sent to the embedding server      |
| `collection` | `None`   | Restrict to one collection; `None` = search all  |
| `top_k`      | `5`      | Maximum number of results                         |
| `filter`     | `None`   | Equality-filter dict (`{"file_path": "..."}`)     |

```python
"""You are a helpful assistant. Answer from the documents."""

with Search(input_text):
    response = prompt()
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

## `with MessageHistory(n)`

Limits the conversation history visible to `prompt()` calls inside the block
to the last `n` user+assistant turn pairs. On exit the full history is
restored.

```python
with MessageHistory(3):
    response = prompt()  # sees only the last 3 turns
```

Use this to control context length or focus the LLM on recent turns.

---

## `with McpServer(url)`

Connects to an MCP server and registers its tool schemas for all `prompt()`
calls inside the block.

On `__enter__`:
- Fetches the tool list from the server.
- Adds tool schemas to context — offered to every `prompt()` inside the block.

On `__exit__`:
- Removes tool schemas from context.
- Flushes any pending (in-flight) tool calls.

```python
"""You are a helpful assistant."""

with McpServer("http://tool-server:8000"):
    prompt()  # LLM sees tool schemas; selects and dispatches

response = prompt()  # no tool schemas — LLM synthesises from tool results
```

### Scoping tools with `tools=`

The `tools` keyword limits which of the server's tools are offered inside the
block. Entries are exact tool names or `fnmatch` patterns:

```python
with McpServer(tools=["search__library_search"]):
    prompt()  # LLM sees only the library search tool

with McpServer(tools=["web_search__*", "read_web_page__read_web_page"]):
    prompt()  # LLM sees the web tools only
```

This makes staged tool ladders deterministic: each stage exposes only its own
tools instead of relying on the system prompt to keep the LLM away from the
rest. A pattern that matches no tool is logged as an error (it is a prompt.py
configuration mistake) but the block still runs with whatever did match.

### Startup validation

At startup the agent scans `prompt.py` for `McpServer(...)` calls, extracts
every URL, connects to each server, lists its tools, and stores the results in
Redis. If a server is unreachable or returns zero tools the process exits
immediately.

### Timeouts

Every `prompt()` call is wrapped with a 100-second ceiling:

```
LLM provider
  ↑ 100 s  asyncio.wait_for  (tools_dsl.py)
  ↑ 130 s  HTTP read timeout (eval path only)
```

The MCP httpx client has its own independent 30-second timeout per request.

---

## Context managers — nesting rules

`with` blocks can be nested. Each block mutates the active context on enter
and restores it on exit. `prompt()` always sees the current context at the
time it is called.

```python
with MessageHistory(5):
    with Search(input_text):
        response = prompt()  # sees: last 5 turns + search results + no tools
```

`McpServer` and `Search` can be combined:

```python
with Search(input_text):
    with McpServer("http://tool-server:8000"):
        prompt()  # tool-selection pass; LLM sees search results + tool schemas

response = prompt()  # no search results, no tool schemas
```

---

## `delay(seconds)`

Sleep for *seconds*. Use to pace calls when the provider rate-limits on
tokens-per-minute.

```python
with McpServer("http://tool-server:8000"):
    prompt()
    delay(3)

response = prompt()
```

`delay` is a direct alias for `time.sleep`; fractional seconds are accepted.

---

## `logger`

A pre-configured `logging.Logger` named `prompt_dsl.script.<stem>`. Available
without any import. Use it to trace execution, measure latency, or surface
values during debugging.

```python
logger.info("prompt.py: start — input_text=%r", input_text[:80])
with Search(input_text) as results:
    logger.info("search done — %d results", len(results))
    response = prompt()
```

---

## Examples

### Minimal

```python
"""You are a concise assistant. Always reply in one sentence."""

response = prompt()
```

### Temperature override

```python
"""You are a creative writing assistant."""

response = prompt(temperature=0.9)
```

### RAG — answer from documents

```python
"""You are a helpful assistant. Answer from the documents."""

with Search(input_text):
    response = prompt()
```

### RAG — restricted collection

```python
"""You are a rules lawyer for tabletop RPGs."""

with Search(input_text, collection="shelf1", top_k=3):
    response = prompt()
```

### Tool use — single phase

```python
"""You are a knowledgeable guide."""

with McpServer("http://tool-server:8000"):
    prompt()  # LLM selects and dispatches tools

response = prompt()  # LLM synthesises tool results
```

### Tool use — with pacing

```python
"""You are a knowledgeable guide."""

with McpServer("http://tool-server:8000"):
    prompt()
    delay(3)

response = prompt()
```

### RAG + tools

```python
"""You are a research assistant."""

import os

with McpServer(os.environ["MCP_SERVER_URL"]):
    prompt()  # tool-selection pass

with Search(input_text):
    response = prompt()  # synthesis with search context
```

### Progress notification

```python
"""You are a helpful assistant."""

notify("Searching…")
with Search(input_text):
    response = prompt()
```

### Limited history

```python
"""You are a focused assistant."""

with MessageHistory(3):
    response = prompt()
```

---

## Implementation

The DSL runtime lives in `agent_stem/src/common/prompt_dsl.py`:

| Symbol                    | Description                                           |
|---------------------------|-------------------------------------------------------|
| `PromptResult`            | Return type of `execute_prompt_script`                |
| `Search`                  | Context manager — injects retrieval results           |
| `MessageHistory`          | Context manager — limits conversation history         |
| `find_prompt_script()`    | Locates `prompt.py` / `agent.py` under `cortex/chat/` |
| `execute_prompt_script()` | Entry point called by `agent_chat.py` on each request |

Tool and context primitives live in `agent_stem/src/common/tools_dsl.py`:

| Symbol                    | Description                                                   |
|---------------------------|---------------------------------------------------------------|
| `DslRunContext`           | Mutable context shared across all DSL objects for one request |
| `McpServer`               | Context manager — connects to MCP server, registers tools     |
| `make_prompt_fn()`        | Creates the `prompt()` callable                               |
| `make_notify_fn()`        | Creates the `notify()` callable                               |

Startup logic lives in `agent_stem/src/startup/mcp_startup.py`:

| Symbol                   | Description                                              |
|--------------------------|----------------------------------------------------------|
| `discover_mcp_servers()` | Scans `prompt.py`, connects to MCP servers, dies on error |

---

# Evaluation DSL

The evaluation DSL follows the same philosophy: place `cortex/chat/eval.py`
next to `prompt.py` to enable the `POST /private/v1/agent/evaluate` API.

The module docstring becomes the suite name. `eval(...)` at module level
configures the run. Every non-underscore function is a test case.

```python
"""My eval suite."""

eval(repeat=2, threshold=1)

def greets_user():
    with question("Hello!"):
        expect(r"(?i)hello|hi")

def remembers_name():
    assume("My name is Alice.")
    with question("What is my name?"):
        expect(r"(?i)\bAlice\b")
```

## Injected globals

| Name | Description |
|---|---|
| `eval(...)` | Suite-level config: `repeat`, `threshold`, `model`, `judge_model`, `delay` |
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

The eval DSL runtime lives in `agent_stem/src/common/eval_dsl.py`:

| Symbol | Description |
|---|---|
| `SuiteConfig` | Dataclass for `eval()` configuration |
| `ParsedSuite` | Result of parsing an `eval.py` script |
| `StepContext` | Context manager for `with step():` blocks |
| `find_eval_script()` | Locates `eval.py` under `cortex/chat/` |
| `parse_eval_script()` | Collects cases and config without executing LLM calls |
| `run_eval_suite()` | Entry point called by the POST endpoint handler |

---

# Future Plans

1. **Streamable `print()`** — `print()` currently buffers and delivers its output only after the script
   finishes.  The plan is to make it stream tokens to the client in real time, matching the behaviour
   of `prompt()`.

2. **Customisable search formatting** — `Search` currently formats results as
   `[file_path | section_title]\ntext`.  A future `format=` parameter (callable or template string)
   will let scripts control exactly how results are presented to the LLM.

3. **Mutable `MessageHistory`** — The `MessageHistory` context manager currently provides a read-only
   window into history.  The plan is to expose a mutable list so scripts can add, remove, or reorder
   turns before passing them to the LLM.

