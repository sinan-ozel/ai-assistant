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

When the agent runs in interactive mode (DSL `prompt.py` uses `notify()`), each
`notify()` call emits one complete chunk with `"notify": true`.  Regular LLM
delta chunks do not include this field.  Clients may use `"notify"` to
distinguish intermediate progress messages from final response tokens — the
Streamlit UI renders them in a collapsible **🤔** expander.

**Responses:** `200 OK`, `408 Request Timeout`, `422 Unprocessable Entity`, `503 Service Unavailable` (no provider configured)

#### Agent customization — `cortex/chat/prompt.py`

`/v1/agent/chat` is the only endpoint that supports agent customization. The other two endpoints (`/v1/chat/completions` and `/v1/api/generate`) are straightforward LiteLLM proxies with no customization layer.

Place a file at `cortex/chat/prompt.py` to customize the agent. The module-level docstring becomes the system message, and the rest of the file is a Python script that runs on every request with access to the full prompt DSL.

**System message via docstring.** The module-level docstring becomes the system message for every conversation:

```python
# cortex/chat/prompt.py

"""
You are a helpful assistant called "Son of Anton".
When your name is asked, respond with "I am Son of Anton, your ever-faithful assistant."
You were designed in Silicon Valley and specialize in debugging code and finding low-cost hamburgers.
"""
```

If `cortex/chat/prompt.py` is absent, the endpoint uses a built-in default system message: `"You are a helpful assistant. You have access to conversation history and can maintain context across messages."`

The `DEFAULT_SYSTEM_MESSAGE` environment variable can also override the default without creating a file.

#### Prompt DSL

The body of `prompt.py` is a Python script that runs on every request. The following globals are injected at request time:

| Name | Description |
|---|---|
| `prompt(...)` | Call the LLM and stream the response. Accepts optional `temperature`, `model`, `max_tokens`, `images`, `system_message`. Handles tool dispatch internally. |
| `notify(text)` | Stream `text` to the client immediately as an intermediate chunk. |
| `Search(query, collection?, top_k?)` | Context manager. Retrieves relevant documents and injects them into the LLM context for the enclosed `prompt()` call. |
| `McpServer(url)` | Context manager. Connects to an external MCP server; its tools are available to `prompt()` calls within the block. |
| `MessageHistory(n?)` | Context manager. Injects the last `n` conversation turns into the LLM context. |
| `delay(seconds)` | Sleep for the given number of seconds. |
| `logger` | Standard Python logger for the agent module. |
| `input_text` / `input()` | The current user message. |

Example — MCP tool agent:

```python
# cortex/chat/prompt.py

"""You are a guide to the world of Eberron."""

with McpServer("http://tool-server:8000"):
    prompt()
```

Example — search-augmented agent with intermediate notification:

```python
# cortex/chat/prompt.py

"""You are a research assistant."""

notify("Searching the library...")
with Search(input()):
    prompt()
```

The agent validates all `McpServer` URLs at startup and refuses to start if
any are unreachable or return zero tools. Discovered tools are listed in the
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
