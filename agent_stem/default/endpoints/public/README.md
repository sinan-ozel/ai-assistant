# Public Endpoints

Three public endpoints are available. All of them route requests through the active LLM provider.

## Provider selection

Every endpoint uses `default.yaml` unless `DEFAULT_PROVIDER` is set to something else.

```
DEFAULT_PROVIDER=coding  # uses cortex/providers/coding.yaml
```

If `DEFAULT_PROVIDER` is not set, the file named `default.yaml` inside `cortex/providers/` is used. If that file does not exist either, the built-in fallback requires `MISTRAL_API_KEY` to be set.

## Provider configuration takes precedence

All LLM parameters — model, api_base, api_key, timeout, temperature, etc. — are set in the provider YAML. **Request body values for these parameters are ignored when the YAML has them.**

Values in YAML files can reference environment variables using `${}` syntax:

```yaml
# cortex/providers/my-provider.yaml
api_base: https://api.mistral.ai
model: mistral/mistral-large-2512
api_key: ${MISTRAL_API_KEY}
timeout: 60
```

This lets you use the same YAML across environments (dev/staging/prod) while varying secrets and endpoints via environment variables.

Supported YAML fields (all optional except `model`):

| Field | Type | Description |
|---|---|---|
| `model` | string | Model name with optional provider prefix, e.g. `mistral/open-mistral-7b` |
| `api_base` | string | Custom API base URL |
| `api_key` | string | API key, can use `${ENV_VAR}` |
| `timeout` | number | Request timeout in seconds |
| `temperature` | number | Sampling temperature (0.0–2.0) |
| `max_tokens` | integer | Maximum tokens to generate |

---

## Endpoints

### `POST /v1/chat/completions` — OpenAI-compatible

Follows the [OpenAI Chat Completions API](https://platform.openai.com/docs/api-reference/chat) format. Drop-in compatible with the OpenAI SDK, LiteLLM (`openai/` prefix), and any OpenAI-compatible client.

**Request body:**

| Field | Type | Default | Description |
|---|---|---|---|
| `messages` | array | required | Chat messages in `[{"role": "user", "content": "..."}]` format |
| `model` | string | — | Requested model. Ignored if provider YAML specifies a model. |
| `stream` | boolean | `false` | Stream response token by token |
| `stream_format` | `"sse"` \| `"ndjson"` | `"sse"` | Streaming wire format |
| `timeout` | number | — | Per-request timeout in seconds (15–300). Overridden by provider YAML. |

**Streaming formats:**
- `sse` (default): Server-Sent Events, OpenAI-compatible (`data: {...}\n\n`, ends with `data: [DONE]\n\n`)
- `ndjson`: Newline-delimited JSON, Ollama-style

**Responses:** `200 OK`, `408 Request Timeout`, `422 Unprocessable Entity`, `501 Not Implemented`

---

### `POST /v1/api/generate` — Ollama-compatible

Follows the [Ollama Generate API](https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion) format. Compatible with Ollama clients and LiteLLM (`ollama/` prefix).

Streaming is not yet supported (`stream: true` returns `501`).

**Request body:**

| Field | Type | Default | Description |
|---|---|---|---|
| `model` | string | required | Model name. Ignored if provider YAML specifies a model. |
| `prompt` | string | required | Text prompt |
| `stream` | boolean | `false` | Not yet implemented |
| `temperature` | number | 0.8 | Overridden by provider YAML. |
| `top_p` | number | 0.9 | Overridden by provider YAML. |
| `top_k` | integer | 40 | Overridden by provider YAML. |
| `timeout` | number | — | Per-request timeout in seconds. Overridden by provider YAML. |

**Responses:** `200 OK`, `408 Request Timeout`, `422 Unprocessable Entity`, `501 Not Implemented` (streaming)

---

### `POST /v1/agent/chat` — Stateful conversation (custom format)

Proprietary endpoint. Maintains per-user, per-conversation message history in Redis. Automatically fits history to the provider's context window.

No standard client compatibility — use directly.

**Request body:**

| Field | Type | Default | Description |
|---|---|---|---|
| `message` | string | required | The user's message |
| `conversation_id` | string | auto-generated | Conversation identifier. Reuse to continue a conversation. |
| `user_id` | string | `"default-user"` | User identifier for memory isolation |
| `stream` | boolean | `false` | Stream response token by token |
| `stream_format` | `"sse"` \| `"ndjson"` | `"sse"` | Streaming wire format |
| `timeout` | number | `180` | Per-request timeout in seconds (15–300). Overridden by provider YAML. |
| `max_tokens` | integer | — | Maximum tokens to generate. Overridden by provider YAML. |

**Streaming formats:** same as `/v1/chat/completions` above, but chunks include `conversation_id`, `user_id`, and `delta`.

**Responses:** `200 OK`, `408 Request Timeout`, `422 Unprocessable Entity`, `503 Service Unavailable` (no provider configured)

#### Agent customization — `cortex/chat/prompt.py`

`/v1/agent/chat` is the only endpoint that supports agent customization. The other two endpoints (`/v1/chat/completions` and `/v1/api/generate`) are straightforward LiteLLM proxies with no customization layer.

Place a file at `cortex/chat/prompt.py` to customize the agent. Currently one customization is implemented:

**System message via docstring.** The module-level docstring becomes the system message for every conversation:

```python
# cortex/chat/prompt.py

"""
You are a helpful assistant called "Son of Anton".
When your name is asked, respond with "I am Son of Anton, your ever-faithful assistant."
You were designed in Silicon Valley and specialize in debugging code and finding low-cost hamburgers.
"""

# The rest of the file is executed but not used yet.
# The input message is passed through unchanged.
```

If `cortex/chat/prompt.py` is absent, the endpoint uses a built-in default system message: `"You are a helpful assistant. You have access to conversation history and can maintain context across messages."`

The `DEFAULT_SYSTEM_MESSAGE` environment variable can also override the default without creating a file.

#### Interactive mode — MCP tools

When `prompt.py` contains any of `llm`, `notify`, `McpServer`, or `mcp`, the
endpoint runs in **interactive mode**.  The script drives the LLM calls and
tool invocations explicitly.

```python
# cortex/chat/prompt.py

"""You are a guide to the world of Eberron."""

with McpServer("http://tool-server:8000") as tools:
    tools.call_read_only()
    tools.wait()
    response = llm()

notify(response)
```

Injected globals available only in interactive mode:

| Name         | Description                                                         |
|--------------|---------------------------------------------------------------------|
| `llm()`      | Call the LLM; returns the assistant response as a string            |
| `notify(text)`| Stream `text` to the client immediately; last call sets final response |
| `McpServer(url)` | Context manager; connects to an MCP server and manages tool calls |
| `mcp`        | Alias for `McpServer`                                               |

`McpServer` methods:

| Method             | Description                                                          |
|--------------------|----------------------------------------------------------------------|
| `call_read_only()` | Submit tools annotated `readOnlyHint=true` concurrently             |
| `call_all()`       | Submit all available tools concurrently                              |
| `wait()`           | Wait for pending tool calls; appends results to message history      |

The agent validates all `McpServer` URLs at startup and refuses to start if
any are unreachable or return zero tools.  Discovered tools are listed in the
Streamlit UI under "External Tools".

---

## Format compatibility summary

| Endpoint | Standard | Compatible clients |
|---|---|---|
| `POST /v1/chat/completions` | OpenAI Chat Completions API | OpenAI SDK, LiteLLM (`openai/` prefix), any OpenAI-compatible client |
| `POST /v1/api/generate` | Ollama Generate API | Ollama clients, LiteLLM (`ollama/` prefix) |
| `POST /v1/agent/chat` | Custom | None — proprietary format |

| Endpoint | SSE (`stream=true`) | NDJSON (`stream_format=ndjson`) |
|---|---|---|
| `POST /v1/chat/completions` | Yes — OpenAI-compatible | Yes — Ollama-style |
| `POST /v1/api/generate` | No | No |
| `POST /v1/agent/chat` | Yes | Yes |
