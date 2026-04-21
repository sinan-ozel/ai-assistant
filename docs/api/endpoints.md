# API Endpoints

agent-stem exposes three public endpoints and several private endpoints.
All endpoints are documented in the interactive Swagger UI at `http://localhost:8000/docs`.

## Public endpoints

### `POST /v1/agent/chat` — Stateful agent conversation

The main agent endpoint. Maintains per-user, per-conversation history in Redis.
Context is automatically trimmed to fit the provider's context window.

```bash
curl -X POST http://localhost:8000/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the capital of France?",
    "conversation_id": "my-session-123",
    "user_id": "alice"
  }'
```

**Request body:**

| Field | Type | Default | Description |
|---|---|---|---|
| `message` | string | required | The user's message |
| `conversation_id` | string | auto-generated | Reuse to continue a conversation |
| `user_id` | string | `"default-user"` | User identifier for memory isolation |
| `stream` | boolean | `false` | Stream response token by token |
| `stream_format` | `"sse"` \| `"ndjson"` | `"sse"` | Wire format for streaming |
| `timeout` | number | `180` | Per-request timeout in seconds |
| `max_tokens` | integer | — | Maximum tokens to generate |

**Streaming response chunk:**
```json
{"conversation_id": "my-session-123", "user_id": "alice", "delta": "Paris"}
```

---

### `POST /v1/chat/completions` — OpenAI-compatible

Drop-in compatible with the OpenAI SDK and any OpenAI-compatible client.

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

**Request body:** Standard OpenAI Chat Completions format. `model` is accepted but
may be ignored if the provider YAML specifies a model.

---

### `POST /v1/api/generate` — Ollama-compatible

Compatible with Ollama clients and LiteLLM (`ollama/` prefix).

```bash
curl -X POST http://localhost:8000/v1/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "gemma3", "prompt": "Hello!"}'
```

Streaming is not yet supported (`stream: true` returns `501`).

---

### Workflow endpoints

Each workflow YAML creates a POST endpoint at the path declared in the YAML:

```bash
curl -X POST http://localhost:8000/v1/summarize-text \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Long text..."}]}'
```

---

## Private endpoints

Private endpoints expose operational and evaluation functionality. They are not
part of the public API and may change between releases.

### `GET /health`

Returns `{"status": "ok"}` when the service is running.

### `GET /private/v1/books`

Lists all indexed documents. Returns each document with its collection (`tags`) and `chunk_count`.

```bash
curl http://localhost:8000/private/v1/books
```

### `POST /private/v1/search`

Direct vector search over the document library. Streaming NDJSON response.

```bash
curl -X POST http://localhost:8000/private/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "psionic powers", "collection": "shelf1", "top_k": 5}'
```

### `POST /private/v1/agent/evaluate`

Start an evaluation run (see [Agent Eval DSL](../eval_dsl.md)).

### `GET /private/v1/agent/evaluate`

Poll for evaluation results.

### `DELETE /private/v1/agent/evaluate`

Cancel the in-progress evaluation run.

### `POST /private/evaluate{path}`

Run evaluation for a workflow. `path` must match a workflow's declared `path` field.

```bash
curl -X POST http://localhost:8000/private/evaluate/v1/extract-nutrition-information
```

---

## Format compatibility summary

| Endpoint | Standard | Compatible clients |
|---|---|---|
| `POST /v1/chat/completions` | OpenAI Chat Completions | OpenAI SDK, LiteLLM, any OpenAI-compatible client |
| `POST /v1/api/generate` | Ollama Generate API | Ollama clients, LiteLLM (`ollama/`) |
| `POST /v1/agent/chat` | Custom | Direct HTTP only |
| `POST /v1/*` (workflows) | Custom | Direct HTTP only |
