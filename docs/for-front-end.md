# Integrating the Agent Chat Endpoint

Reference for front-end developers connecting to `POST /v1/agent/chat`.

---

## Conversation identity

Every request belongs to a `(user_id, conversation_id)` pair.

| Field | How to supply it | Notes |
|---|---|---|
| `user_id` | Inject via `User-Id` request header (preferred) or `user_id` body field | Header takes precedence; body field is a fallback for direct clients |
| `conversation_id` | Omit to start a new thread; pass the value returned in the previous response to continue | The server generates a UUID when omitted |

```json
{
  "message": "Hello!",
  "user_id": "alice",
  "conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

The server automatically trims conversation history to fit the configured
context window, so you never need to manage history on the client side.

---

## Non-streaming

Set `stream: false` (default). The response arrives as a single JSON object
once the full reply is ready.

**Request:**
```json
{
  "message": "What is the capital of France?",
  "user_id": "alice"
}
```

**Response `200 OK`:**
```json
{
  "conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "user_id": "alice",
  "message": "The capital of France is Paris.",
  "role": "assistant",
  "created": 1703347200,
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 9,
    "total_tokens": 29
  }
}
```

---

## Streaming

Set `stream: true`. The server opens a persistent HTTP connection and pushes
chunks as the model generates tokens.

Two wire formats are available:

| `stream_format` | Content-Type | Terminator |
|---|---|---|
| `"sse"` (default) | `text/event-stream` | `data: [DONE]\n\n` |
| `"ndjson"` | `application/x-ndjson` | `{"done": true}\n` |

### SSE format

Each chunk is delivered as:

```
data: {"conversation_id":"...","user_id":"alice","role":"assistant","created":1703347200,"delta":{"content":"Paris"},"finish_reason":null}\n\n
```

The stream ends with:

```
data: [DONE]\n\n
```

### NDJSON format

Each chunk is a complete JSON object on its own line:

```
{"conversation_id":"...","user_id":"alice","role":"assistant","created":1703347200,"delta":{"content":"Paris"},"finish_reason":null}
```

The stream ends with:

```
{"done": true}
```

### Chunk fields

| Field | Type | Always present | Description |
|---|---|---|---|
| `conversation_id` | string | yes | Conversation identifier; pass back on the next turn |
| `user_id` | string | yes | User identifier |
| `role` | string | yes | Always `"assistant"` |
| `created` | integer | yes | Unix timestamp of the request |
| `delta` | object | yes | `{"content": "<token>"}` when the chunk carries LLM tokens; `{}` on the final chunk |
| `finish_reason` | string\|null | yes | `null` on intermediate chunks; `"stop"` on the final token chunk |
| `notify` | boolean | no | Present and `true` only on notify chunks (see below) |
| `error` | string | no | Present only when `finish_reason` is `"error"` |

---

## Notify chunks

When the agent's DSL script calls `notify(text)`, the server emits a chunk
**before** the LLM response tokens begin. Notify chunks carry a complete
message — they are not incremental tokens. They are identified by the
`"notify": true` field.

```json
{
  "conversation_id": "...",
  "user_id": "alice",
  "role": "assistant",
  "created": 1703347200,
  "delta": {"content": "Searching documents…"},
  "finish_reason": null,
  "notify": true
}
```

**Recommended handling:**

1. Check each chunk for `"notify": true`.
2. If present, add the `delta.content` text to a collapsible "thinking"
   indicator (e.g. a spinner or expander). Do **not** append it to the
   visible reply.
3. If absent, append `delta.content` to the visible reply as normal.

Regular delta chunks (LLM tokens) never include the `notify` field.

---

## Parsing SSE in JavaScript

```js
async function streamChat(message, conversationId, userId) {
  const resp = await fetch('/v1/agent/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      user_id: userId,
      stream: true,
      stream_format: 'sse',
    }),
  });

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let reply = '';
  const thinkingParts = [];

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop(); // keep incomplete last line

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      const data = line.slice(6).trim();
      if (data === '[DONE]') return { reply, thinkingParts };

      const chunk = JSON.parse(data);
      const content = chunk.delta?.content;
      if (!content) continue;

      if (chunk.notify) {
        thinkingParts.push(content);   // show in collapsible "thinking" UI
      } else {
        reply += content;              // append to visible response
      }
    }
  }
  return { reply, thinkingParts };
}
```

---

## Conversation continuity

The `conversation_id` returned in the first response (or in the first
streaming chunk) must be sent back on subsequent requests to continue the
thread:

```js
let conversationId = null;

async function chat(message) {
  const { reply, conversationId: newId } = await streamChat(
    message, conversationId, 'alice'
  );
  conversationId = newId;  // persist for next turn
  return reply;
}
```

---

## Error handling

### HTTP errors (before the stream opens)

| Status | Meaning |
|---|---|
| `422` | Validation error — inspect `detail` in the response body |
| `408` | LLM provider timed out |
| `503` | No provider configured |

### Errors mid-stream

If the LLM connection drops after the stream has started, the server emits
an error chunk and then closes the stream:

```json
{
  "conversation_id": "...",
  "delta": {},
  "finish_reason": "error",
  "error": "Connection reset by peer"
}
```

For SSE, `data: [DONE]\n\n` follows immediately. For NDJSON, the error chunk
itself carries `"done": true`.

Always check `finish_reason` on the final chunk. If it is `"error"`, surface
the `error` field to the user.
