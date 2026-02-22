# OpenAPI Contract Test Report

## Summary

- **Total Tests:** 36
- **Passed:** ✅ 36
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
  "available_providers": 1
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
    "ollama_on_tailscale"
  ],
  "default": "ollama_on_tailscale",
  "total": 12,
  "status": "one_provider_available"
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
  "message": "Okay, let\u2019s check the weather for **London, England**! \u2600\ufe0f\ud83c\udf27\ufe0f\ud83c\udf2c\ufe0f",
  "role": "assistant",
  "created": 1771730172,
  "usage": {
    "prompt_tokens": 3926,
    "completion_tokens": 22,
    "total_tokens": 3948
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
  "id": "chatcmpl-5b02731bcfbd41dd9fe06a54",
  "object": "chat.completion",
  "created": 1771730198,
  "model": "ollama/gemma3:1b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "###The capital of France is **Paris**. \n\nIt\u2019s a bit of a complicated question \u2013 Paris is officially the capital, but the \u201ccapital\u201d of France is often debated. The historical capital was Lyon, but it was moved to Paris in 1800. \n\nBut, as it stands today, Paris is the official and recognized capital. \ud83d\ude0a"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 21,
    "completion_tokens": 75,
    "total_tokens": 96
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
  "id": "chatcmpl-34e0310db4c7439e881f0e00",
  "object": "chat.completion",
  "created": 1771730202,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic opening line of Lorem Ipsum \u2013 the placeholder text used in printing and design. \n\nIs there anything you'd like me to do with this text? For example, would you like me to:\n\n*   **Analyze it?** (e.g., its purpose, common interpretations)\n*   **Generate something with it?** (e.g., a short story, a poem, a description)\n*   **Explain its significance?**\n*   **Just acknowledge it?**"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 114,
    "total_tokens": 133
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
  "id": "chatcmpl-557adb2e841e4a08952c6e2b",
  "object": "chat.completion",
  "created": 1771730203,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the standard placeholder text: \"Lorem ipsum dolor sit amet\". \n\nIt's a common practice in typesetting and design to use this text to demonstrate the visual appearance of a document without relying on actual content. \n\nIs there anything you'd like me to do with this text? For example, would you like me to:\n\n*   Analyze it?\n*   Generate a similar text?\n*   Do something else with it?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 100,
    "total_tokens": 119
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
  "created_at": "2026-02-22T03:16:44.598916Z",
  "response": "The capital of France is **Paris**. \n\nIt\u2019s a great city! \ud83d\ude0a \n\nDo you want to know more about Paris?",
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
