# OpenAPI Contract Test Report

## Summary

- **Total Tests:** 47
- **Passed:** ✅ 47
- **Failed:** ❌ 0

---

## Test #1 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `GET /health`

### Expected Response

**Status:** `200`

```json
{
  "status": "ok",
  "providers_loading": false,
  "available_providers": 1
}
```

### Actual Response

**Status:** `200`

```json
{
  "status": "ok",
  "providers_loading": false,
  "available_providers": 12
}
```

---

## Test #2 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `GET /private/v1/providers/{provider}/max-context-window`

### Expected Response

**Status:** `200 or 404 or 422`

```json
{
  "provider": "pixtral",
  "max_context_window": 128000
}
```

### Actual Response

**Status:** `404`

```json
{
  "detail": "Provider '{provider}' not found"
}
```

---

## Test #3 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `GET /private/v1/providers`

### Expected Response

**Status:** `200`

```json
{
  "available": [
    "pixtral",
    "gemma3_on_vpn"
  ],
  "default": "pixtral",
  "total": 2,
  "status": "multiple_providers_available"
}
```

### Actual Response

**Status:** `200`

```json
{
  "available": [
    "codestral",
    "magistral-small",
    "ministral-14b",
    "ministral-3b",
    "ministral-8b",
    "mistral-7b",
    "mistral-large",
    "mistral-small",
    "pixtral",
    "voxtral-mini",
    "voxtral-small",
    "ollama_on_tailscale"
  ],
  "default": "ollama_on_tailscale",
  "total": 12,
  "status": "multiple_providers_available"
}
```

---

## Test #4 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "What's the weather?",
  "conversation_id": "conv-123",
  "user_id": "user-456",
  "stream": false,
  "stream_format": "sse"
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 503 or 408`

```json
{
  "conversation_id": "conv-123",
  "user_id": "user-456",
  "message": "The weather is sunny today!",
  "role": "assistant",
  "created": 1703347200,
  "usage": {
    "prompt_tokens": 56,
    "completion_tokens": 31,
    "total_tokens": 87
  }
}
```

### Actual Response

**Status:** `200`

```json
{
  "conversation_id": "conv-123",
  "user_id": "user-456",
  "message": "Okay! I need your current location to give you the weather. Where are you? \ud83d\ude0a",
  "role": "assistant",
  "created": 1771730597,
  "usage": {
    "prompt_tokens": 1098,
    "completion_tokens": 19,
    "total_tokens": 1117
  }
}
```

---

## Test #5 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "stream_format": "sse",
  "timeout": 0.0,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 503 or 408`

```json
{
  "conversation_id": "conv-123",
  "user_id": "user-456",
  "message": "The weather is sunny today!",
  "role": "assistant",
  "created": 1703347200,
  "usage": {
    "prompt_tokens": 56,
    "completion_tokens": 31,
    "total_tokens": 87
  }
}
```

### Actual Response

**Status:** `200`

```json
"[Streaming response: text/event-stream; charset=utf-8]"
```

---

## Test #6 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "stream_format": "sse",
  "timeout": 0.0,
  "max_tokens": 500000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 503 or 408`

```json
{
  "conversation_id": "conv-123",
  "user_id": "user-456",
  "message": "The weather is sunny today!",
  "role": "assistant",
  "created": 1703347200,
  "usage": {
    "prompt_tokens": 56,
    "completion_tokens": 31,
    "total_tokens": 87
  }
}
```

### Actual Response

**Status:** `200`

```json
"[Streaming response: text/event-stream; charset=utf-8]"
```

---

## Test #7 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "stream_format": "sse",
  "timeout": 0.0,
  "max_tokens": 1000000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 503 or 408`

```json
{
  "conversation_id": "conv-123",
  "user_id": "user-456",
  "message": "The weather is sunny today!",
  "role": "assistant",
  "created": 1703347200,
  "usage": {
    "prompt_tokens": 56,
    "completion_tokens": 31,
    "total_tokens": 87
  }
}
```

### Actual Response

**Status:** `200`

```json
"[Streaming response: text/event-stream; charset=utf-8]"
```

---

## Test #8 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "stream_format": "sse",
  "timeout": 0.123456789,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 503 or 408`

```json
{
  "conversation_id": "conv-123",
  "user_id": "user-456",
  "message": "The weather is sunny today!",
  "role": "assistant",
  "created": 1703347200,
  "usage": {
    "prompt_tokens": 56,
    "completion_tokens": 31,
    "total_tokens": 87
  }
}
```

### Actual Response

**Status:** `200`

```json
"[Streaming response: text/event-stream; charset=utf-8]"
```

---

## Test #9 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "stream_format": "sse",
  "timeout": 0.123456789,
  "max_tokens": 500000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 503 or 408`

```json
{
  "conversation_id": "conv-123",
  "user_id": "user-456",
  "message": "The weather is sunny today!",
  "role": "assistant",
  "created": 1703347200,
  "usage": {
    "prompt_tokens": 56,
    "completion_tokens": 31,
    "total_tokens": 87
  }
}
```

### Actual Response

**Status:** `200`

```json
"[Streaming response: text/event-stream; charset=utf-8]"
```

---

## Test #10 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "stream_format": "sse",
  "timeout": 0.123456789,
  "max_tokens": 1000000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 503 or 408`

```json
{
  "conversation_id": "conv-123",
  "user_id": "user-456",
  "message": "The weather is sunny today!",
  "role": "assistant",
  "created": 1703347200,
  "usage": {
    "prompt_tokens": 56,
    "completion_tokens": 31,
    "total_tokens": 87
  }
}
```

### Actual Response

**Status:** `200`

```json
"[Streaming response: text/event-stream; charset=utf-8]"
```

---

## Test #11 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "stream_format": "sse",
  "timeout": 0.999999999,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 503 or 408`

```json
{
  "conversation_id": "conv-123",
  "user_id": "user-456",
  "message": "The weather is sunny today!",
  "role": "assistant",
  "created": 1703347200,
  "usage": {
    "prompt_tokens": 56,
    "completion_tokens": 31,
    "total_tokens": 87
  }
}
```

### Actual Response

**Status:** `200`

```json
"[Streaming response: text/event-stream; charset=utf-8]"
```

---

## Test #12 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "stream_format": "sse",
  "timeout": 0.999999999,
  "max_tokens": 500000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 503 or 408`

```json
{
  "conversation_id": "conv-123",
  "user_id": "user-456",
  "message": "The weather is sunny today!",
  "role": "assistant",
  "created": 1703347200,
  "usage": {
    "prompt_tokens": 56,
    "completion_tokens": 31,
    "total_tokens": 87
  }
}
```

### Actual Response

**Status:** `200`

```json
"[Streaming response: text/event-stream; charset=utf-8]"
```

---

## Test #13 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "stream_format": "sse",
  "timeout": 0.999999999,
  "max_tokens": 1000000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 503 or 408`

```json
{
  "conversation_id": "conv-123",
  "user_id": "user-456",
  "message": "The weather is sunny today!",
  "role": "assistant",
  "created": 1703347200,
  "usage": {
    "prompt_tokens": 56,
    "completion_tokens": 31,
    "total_tokens": 87
  }
}
```

### Actual Response

**Status:** `200`

```json
"[Streaming response: text/event-stream; charset=utf-8]"
```

---

## Test #14 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "stream_format": "sse",
  "timeout": 1.111111111,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 503 or 408`

```json
{
  "conversation_id": "conv-123",
  "user_id": "user-456",
  "message": "The weather is sunny today!",
  "role": "assistant",
  "created": 1703347200,
  "usage": {
    "prompt_tokens": 56,
    "completion_tokens": 31,
    "total_tokens": 87
  }
}
```

### Actual Response

**Status:** `200`

```json
"[Streaming response: text/event-stream; charset=utf-8]"
```

---

## Test #15 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/chat/completions`

### Request Body

```json
{
  "messages": [
    {
      "role": "user",
      "content": "What is the capital of France?"
    }
  ],
  "stream": false
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1734700000,
  "model": "pixtral",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 10,
    "total_tokens": 30
  }
}
```

### Actual Response

**Status:** `200`

```json
{
  "id": "chatcmpl-40805086b7474a17b3f2657c",
  "object": "chat.completion",
  "created": 1771730619,
  "model": "ollama/gemma3:1b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is **Paris**. \n\nDo you want to know more about Paris, like its history or famous landmarks?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 21,
    "completion_tokens": 27,
    "total_tokens": 48
  }
}
```

---

## Test #16 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/chat/completions`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "messages": [
    {
      "role": "system",
      "content": "Lorem ipsum dolor sit amet"
    }
  ],
  "timeout": 0.0,
  "stream": true,
  "stream_format": "sse"
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1734700000,
  "model": "pixtral",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 10,
    "total_tokens": 30
  }
}
```

### Actual Response

**Status:** `200`

```json
"[Streaming response: text/event-stream; charset=utf-8]"
```

---

## Test #17 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/chat/completions`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "messages": [
    {
      "role": "system",
      "content": "Lorem ipsum dolor sit amet"
    }
  ],
  "timeout": 0.0,
  "stream": true,
  "stream_format": "ndjson"
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1734700000,
  "model": "pixtral",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 10,
    "total_tokens": 30
  }
}
```

### Actual Response

**Status:** `200`

```json
"[Streaming response: application/x-ndjson]"
```

---

## Test #18 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/chat/completions`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "messages": [
    {
      "role": "system",
      "content": "Lorem ipsum dolor sit amet"
    }
  ],
  "timeout": 0.0,
  "stream": true,
  "stream_format": "invalid_enum_value"
}
```

### Expected Response

**Status:** `400 or 422 or 200 or 404 or 501 or 408`

```json
"400/422 (invalid enum value)"
```

### Actual Response

**Status:** `422`

```json
{
  "detail": "'invalid_enum_value' is not one of ['sse', 'ndjson']\n\nFailed validating 'enum' in schema['properties']['stream_format']:\n    {'type': 'string',\n     'enum': ['sse', 'ndjson'],\n     'default': 'sse',\n     'description': \"Streaming format: 'sse' for Server-Sent Events \"\n                    \"(OpenAI-compatible), 'ndjson' for newline-delimited \"\n                    'JSON (Ollama-style)'}\n\nOn instance['stream_format']:\n    'invalid_enum_value'"
}
```

---

## Test #19 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/chat/completions`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "messages": [
    {
      "role": "system",
      "content": "Lorem ipsum dolor sit amet"
    }
  ],
  "timeout": 0.0,
  "stream": false,
  "stream_format": "sse"
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1734700000,
  "model": "pixtral",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 10,
    "total_tokens": 30
  }
}
```

### Actual Response

**Status:** `200`

```json
{
  "id": "chatcmpl-12b7fab942a94506af9dc885",
  "object": "chat.completion",
  "created": 1771730623,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the standard placeholder text. \n\nIs there anything you'd like me to do with it? For example, would you like me to:\n\n*   **Generate more Lorem Ipsum text?** (e.g., a longer passage)\n*   **Explain the purpose of Lorem Ipsum?** (it's used to simulate the reading experience of a document before the actual content is finalized.)\n*   **Convert it to a different format?** (e.g., a Python code snippet, a JSON representation)\n*   **Something else entirely?**"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 126,
    "total_tokens": 145
  }
}
```

---

## Test #20 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/chat/completions`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "messages": [
    {
      "role": "system",
      "content": "Lorem ipsum dolor sit amet"
    }
  ],
  "timeout": 0.0,
  "stream": false,
  "stream_format": "ndjson"
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1734700000,
  "model": "pixtral",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 10,
    "total_tokens": 30
  }
}
```

### Actual Response

**Status:** `200`

```json
{
  "id": "chatcmpl-40e517f8c226404999611297",
  "object": "chat.completion",
  "created": 1771730624,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the standard placeholder text \"Lorem ipsum dolor sit amet\". \n\nIs there anything I can help you with regarding this text? For example, would you like me to:\n\n*   **Analyze it?** (e.g., identify the types of words it contains)\n*   **Generate text based on it?** (e.g., a story, a paragraph, etc.)\n*   **Provide context or explanation?** (e.g., where it's used in a document)\n*   **Something else entirely?**"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 122,
    "total_tokens": 141
  }
}
```

---

## Test #21 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/chat/completions`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "messages": [
    {
      "role": "system",
      "content": "Lorem ipsum dolor sit amet"
    }
  ],
  "timeout": 0.0,
  "stream": false,
  "stream_format": "invalid_enum_value"
}
```

### Expected Response

**Status:** `400 or 422 or 200 or 404 or 501 or 408`

```json
"400/422 (invalid enum value)"
```

### Actual Response

**Status:** `422`

```json
{
  "detail": "'invalid_enum_value' is not one of ['sse', 'ndjson']\n\nFailed validating 'enum' in schema['properties']['stream_format']:\n    {'type': 'string',\n     'enum': ['sse', 'ndjson'],\n     'default': 'sse',\n     'description': \"Streaming format: 'sse' for Server-Sent Events \"\n                    \"(OpenAI-compatible), 'ndjson' for newline-delimited \"\n                    'JSON (Ollama-style)'}\n\nOn instance['stream_format']:\n    'invalid_enum_value'"
}
```

---

## Test #22 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/chat/completions`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "messages": [
    {
      "role": "system",
      "content": "Lorem ipsum dolor sit amet"
    }
  ],
  "timeout": 0.123456789,
  "stream": true,
  "stream_format": "sse"
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1734700000,
  "model": "pixtral",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 10,
    "total_tokens": 30
  }
}
```

### Actual Response

**Status:** `200`

```json
"[Streaming response: text/event-stream; charset=utf-8]"
```

---

## Test #23 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/chat/completions`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "messages": [
    {
      "role": "system",
      "content": "Lorem ipsum dolor sit amet"
    }
  ],
  "timeout": 0.123456789,
  "stream": true,
  "stream_format": "ndjson"
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1734700000,
  "model": "pixtral",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 10,
    "total_tokens": 30
  }
}
```

### Actual Response

**Status:** `200`

```json
"[Streaming response: application/x-ndjson]"
```

---

## Test #24 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/chat/completions`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "messages": [
    {
      "role": "system",
      "content": "Lorem ipsum dolor sit amet"
    }
  ],
  "timeout": 0.123456789,
  "stream": true,
  "stream_format": "invalid_enum_value"
}
```

### Expected Response

**Status:** `400 or 422 or 200 or 404 or 501 or 408`

```json
"400/422 (invalid enum value)"
```

### Actual Response

**Status:** `422`

```json
{
  "detail": "'invalid_enum_value' is not one of ['sse', 'ndjson']\n\nFailed validating 'enum' in schema['properties']['stream_format']:\n    {'type': 'string',\n     'enum': ['sse', 'ndjson'],\n     'default': 'sse',\n     'description': \"Streaming format: 'sse' for Server-Sent Events \"\n                    \"(OpenAI-compatible), 'ndjson' for newline-delimited \"\n                    'JSON (Ollama-style)'}\n\nOn instance['stream_format']:\n    'invalid_enum_value'"
}
```

---

## Test #25 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/chat/completions`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "messages": [
    {
      "role": "system",
      "content": "Lorem ipsum dolor sit amet"
    }
  ],
  "timeout": 0.123456789,
  "stream": false,
  "stream_format": "sse"
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1734700000,
  "model": "pixtral",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 10,
    "total_tokens": 30
  }
}
```

### Actual Response

**Status:** `408`

```json
{
  "detail": "Request timeout: The LLM provider did not respond within the specified timeout period. litellm.APIConnectionError: OllamaException - litellm.Timeout: Connection timed out after 0.123456789 seconds."
}
```

---

## Test #26 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/api/generate`

### Request Body

```json
{
  "model": "gemma3:4b",
  "prompt": "What is the capital of France?",
  "stream": false,
  "temperature": 0.7
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "model": "gemma3:4b",
  "created_at": "2024-12-20T00:00:00.000000Z",
  "response": "The capital of France is Paris.",
  "done": true,
  "context": [],
  "total_duration": 0,
  "load_duration": 0,
  "prompt_eval_count": 10,
  "prompt_eval_duration": 0,
  "eval_count": 10,
  "eval_duration": 0
}
```

### Actual Response

**Status:** `200`

```json
{
  "model": "gemma3:4b",
  "created_at": "2026-02-22T03:23:45.827283Z",
  "response": "The capital of France is **Paris**. \n\nIt\u2019s a very popular question, and it\u2019s easy to get it right! \ud83d\ude0a",
  "done": true,
  "context": [],
  "total_duration": 0,
  "load_duration": 0,
  "prompt_eval_count": 21,
  "prompt_eval_duration": 0,
  "eval_count": 30,
  "eval_duration": 0
}
```

---

## Test #27 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/api/generate`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "prompt": "Lorem ipsum dolor sit amet",
  "stream": true,
  "temperature": 0.0,
  "top_p": 0.0,
  "top_k": 1,
  "timeout": 0.0
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "model": "gemma3:4b",
  "created_at": "2024-12-20T00:00:00.000000Z",
  "response": "The capital of France is Paris.",
  "done": true,
  "context": [],
  "total_duration": 0,
  "load_duration": 0,
  "prompt_eval_count": 10,
  "prompt_eval_duration": 0,
  "eval_count": 10,
  "eval_duration": 0
}
```

### Actual Response

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #28 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/api/generate`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "prompt": "Lorem ipsum dolor sit amet",
  "stream": true,
  "temperature": 0.0,
  "top_p": 0.0,
  "top_k": 1,
  "timeout": 0.123456789
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "model": "gemma3:4b",
  "created_at": "2024-12-20T00:00:00.000000Z",
  "response": "The capital of France is Paris.",
  "done": true,
  "context": [],
  "total_duration": 0,
  "load_duration": 0,
  "prompt_eval_count": 10,
  "prompt_eval_duration": 0,
  "eval_count": 10,
  "eval_duration": 0
}
```

### Actual Response

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #29 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/api/generate`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "prompt": "Lorem ipsum dolor sit amet",
  "stream": true,
  "temperature": 0.0,
  "top_p": 0.0,
  "top_k": 1,
  "timeout": 0.999999999
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "model": "gemma3:4b",
  "created_at": "2024-12-20T00:00:00.000000Z",
  "response": "The capital of France is Paris.",
  "done": true,
  "context": [],
  "total_duration": 0,
  "load_duration": 0,
  "prompt_eval_count": 10,
  "prompt_eval_duration": 0,
  "eval_count": 10,
  "eval_duration": 0
}
```

### Actual Response

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #30 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/api/generate`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "prompt": "Lorem ipsum dolor sit amet",
  "stream": true,
  "temperature": 0.0,
  "top_p": 0.0,
  "top_k": 1,
  "timeout": 1.111111111
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "model": "gemma3:4b",
  "created_at": "2024-12-20T00:00:00.000000Z",
  "response": "The capital of France is Paris.",
  "done": true,
  "context": [],
  "total_duration": 0,
  "load_duration": 0,
  "prompt_eval_count": 10,
  "prompt_eval_duration": 0,
  "eval_count": 10,
  "eval_duration": 0
}
```

### Actual Response

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #31 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/api/generate`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "prompt": "Lorem ipsum dolor sit amet",
  "stream": true,
  "temperature": 0.0,
  "top_p": 0.0,
  "top_k": 1,
  "timeout": 500000.0
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "model": "gemma3:4b",
  "created_at": "2024-12-20T00:00:00.000000Z",
  "response": "The capital of France is Paris.",
  "done": true,
  "context": [],
  "total_duration": 0,
  "load_duration": 0,
  "prompt_eval_count": 10,
  "prompt_eval_duration": 0,
  "eval_count": 10,
  "eval_duration": 0
}
```

### Actual Response

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #32 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/api/generate`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "prompt": "Lorem ipsum dolor sit amet",
  "stream": true,
  "temperature": 0.0,
  "top_p": 0.0,
  "top_k": 1,
  "timeout": 1000000.0
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "model": "gemma3:4b",
  "created_at": "2024-12-20T00:00:00.000000Z",
  "response": "The capital of France is Paris.",
  "done": true,
  "context": [],
  "total_duration": 0,
  "load_duration": 0,
  "prompt_eval_count": 10,
  "prompt_eval_duration": 0,
  "eval_count": 10,
  "eval_duration": 0
}
```

### Actual Response

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #33 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/api/generate`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "prompt": "Lorem ipsum dolor sit amet",
  "stream": true,
  "temperature": 0.0,
  "top_p": 0.0,
  "top_k": 500000,
  "timeout": 0.0
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "model": "gemma3:4b",
  "created_at": "2024-12-20T00:00:00.000000Z",
  "response": "The capital of France is Paris.",
  "done": true,
  "context": [],
  "total_duration": 0,
  "load_duration": 0,
  "prompt_eval_count": 10,
  "prompt_eval_duration": 0,
  "eval_count": 10,
  "eval_duration": 0
}
```

### Actual Response

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #34 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/api/generate`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "prompt": "Lorem ipsum dolor sit amet",
  "stream": true,
  "temperature": 0.0,
  "top_p": 0.0,
  "top_k": 500000,
  "timeout": 0.123456789
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "model": "gemma3:4b",
  "created_at": "2024-12-20T00:00:00.000000Z",
  "response": "The capital of France is Paris.",
  "done": true,
  "context": [],
  "total_duration": 0,
  "load_duration": 0,
  "prompt_eval_count": 10,
  "prompt_eval_duration": 0,
  "eval_count": 10,
  "eval_duration": 0
}
```

### Actual Response

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #35 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/api/generate`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "prompt": "Lorem ipsum dolor sit amet",
  "stream": true,
  "temperature": 0.0,
  "top_p": 0.0,
  "top_k": 500000,
  "timeout": 0.999999999
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "model": "gemma3:4b",
  "created_at": "2024-12-20T00:00:00.000000Z",
  "response": "The capital of France is Paris.",
  "done": true,
  "context": [],
  "total_duration": 0,
  "load_duration": 0,
  "prompt_eval_count": 10,
  "prompt_eval_duration": 0,
  "eval_count": 10,
  "eval_duration": 0
}
```

### Actual Response

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #36 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/api/generate`

### Request Body

```json
{
  "model": "Lorem ipsum dolor sit amet",
  "prompt": "Lorem ipsum dolor sit amet",
  "stream": true,
  "temperature": 0.0,
  "top_p": 0.0,
  "top_k": 500000,
  "timeout": 1.111111111
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501 or 408`

```json
{
  "model": "gemma3:4b",
  "created_at": "2024-12-20T00:00:00.000000Z",
  "response": "The capital of France is Paris.",
  "done": true,
  "context": [],
  "total_duration": 0,
  "load_duration": 0,
  "prompt_eval_count": 10,
  "prompt_eval_duration": 0,
  "eval_count": 10,
  "eval_duration": 0
}
```

### Actual Response

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #37 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/summarize-text`

### Request Body

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Your message here"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 4096,
  "stream": false
}
```

### Expected Response

**Status:** `200 or 429 or 422`

```json
{
  "result": "example",
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

### Actual Response

**Status:** `200`

```json
{
  "result": "Please provide the user message you would like me to summarize. I need the text of the message to fulfill your request.",
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 25,
    "total_tokens": 75
  }
}
```

---

## Test #38 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/summarize-text`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 1,
  "stream": true,
  "stream_format": "sse"
}
```

### Expected Response

**Status:** `200 or 429 or 422`

```json
{
  "result": "example",
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

### Actual Response

**Status:** `422`

```json
{
  "detail": "messages array cannot be empty"
}
```

---

## Test #39 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/summarize-text`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 1,
  "stream": true,
  "stream_format": "ndjson"
}
```

### Expected Response

**Status:** `200 or 429 or 422`

```json
{
  "result": "example",
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

### Actual Response

**Status:** `422`

```json
{
  "detail": "messages array cannot be empty"
}
```

---

## Test #40 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/summarize-text`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 1,
  "stream": true,
  "stream_format": "invalid_enum_value"
}
```

### Expected Response

**Status:** `400 or 200 or 429 or 422`

```json
"400/422 (invalid enum value)"
```

### Actual Response

**Status:** `422`

```json
{
  "detail": "messages array cannot be empty"
}
```

---

## Test #41 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/summarize-text`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 1,
  "stream": false,
  "stream_format": "sse"
}
```

### Expected Response

**Status:** `200 or 429 or 422`

```json
{
  "result": "example",
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

### Actual Response

**Status:** `422`

```json
{
  "detail": "messages array cannot be empty"
}
```

---

## Test #42 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/summarize-text`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 1,
  "stream": false,
  "stream_format": "ndjson"
}
```

### Expected Response

**Status:** `200 or 429 or 422`

```json
{
  "result": "example",
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

### Actual Response

**Status:** `422`

```json
{
  "detail": "messages array cannot be empty"
}
```

---

## Test #43 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/summarize-text`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 1,
  "stream": false,
  "stream_format": "invalid_enum_value"
}
```

### Expected Response

**Status:** `400 or 200 or 429 or 422`

```json
"400/422 (invalid enum value)"
```

### Actual Response

**Status:** `422`

```json
{
  "detail": "messages array cannot be empty"
}
```

---

## Test #44 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/summarize-text`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 500000,
  "stream": true,
  "stream_format": "sse"
}
```

### Expected Response

**Status:** `200 or 429 or 422`

```json
{
  "result": "example",
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

### Actual Response

**Status:** `422`

```json
{
  "detail": "messages array cannot be empty"
}
```

---

## Test #45 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/summarize-text`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 500000,
  "stream": true,
  "stream_format": "ndjson"
}
```

### Expected Response

**Status:** `200 or 429 or 422`

```json
{
  "result": "example",
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

### Actual Response

**Status:** `422`

```json
{
  "detail": "messages array cannot be empty"
}
```

---

## Test #46 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/summarize-text`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 500000,
  "stream": true,
  "stream_format": "invalid_enum_value"
}
```

### Expected Response

**Status:** `400 or 200 or 429 or 422`

```json
"400/422 (invalid enum value)"
```

### Actual Response

**Status:** `422`

```json
{
  "detail": "messages array cannot be empty"
}
```

---

## Test #47 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/summarize-text`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 500000,
  "stream": false,
  "stream_format": "sse"
}
```

### Expected Response

**Status:** `200 or 429 or 422`

```json
{
  "result": "example",
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

### Actual Response

**Status:** `422`

```json
{
  "detail": "messages array cannot be empty"
}
```

---
