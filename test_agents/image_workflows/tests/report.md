# OpenAPI Contract Test Report

## Summary

- **Total Tests:** 69
- **Passed:** ✅ 69
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
    "llama_on_tailscale"
  ],
  "default": "llama_on_tailscale",
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
  "message": "I need to know where you are to check the weather! \ud83d\ude0a Could you please tell me your current location? For example, city name, country, or zip code? \ud83c\udf24\ufe0f",
  "role": "assistant",
  "created": 1771730741,
  "usage": {
    "prompt_tokens": 1143,
    "completion_tokens": 587,
    "total_tokens": 1730
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
  "id": "chatcmpl-7e6176056470451bbfa93c05",
  "object": "chat.completion",
  "created": 1771730789,
  "model": "qwen3-vl:2b-q4km",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is **Paris**.  \n\nThis city has been the political, cultural, and economic heart of France for centuries, serving as the seat of government (including the National Assembly, the Senate, and the President of France). It's also renowned for its iconic landmarks like the Eiffel Tower, Louvre Museum, and Notre-Dame Cathedral.  \n\n*Note: While Paris is the capital, it's also the most famous city in France and a global hub for tourism, arts, and fashion.*"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 17,
    "completion_tokens": 611,
    "total_tokens": 628
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
  "id": "chatcmpl-18bb4169ddcd41b39a4459e8",
  "object": "chat.completion",
  "created": 1771730807,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "It seems like you've pasted placeholder text (\"Lorem ipsum dolor sit amet\") instead of a specific question or request. This is commonly used in design and publishing to represent content without actual text (like \"Lorem ipsum\" in typography).  \n\nIf you have a question or need help with something specific\u2014whether it's writing, design, or another topic\u2014I\u2019d be happy to assist! Just let me know how I can help. \ud83d\ude0a"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 396,
    "total_tokens": 411
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
  "id": "chatcmpl-2a28aa9788c64d59b3c3faed",
  "object": "chat.completion",
  "created": 1771730811,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! I'm here to help. How can I assist you today? \ud83d\ude0a"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 283,
    "total_tokens": 298
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
  "detail": "Request timeout: The LLM provider did not respond within the specified timeout period. litellm.Timeout: APITimeoutError - Request timed out. Error_str: Request timed out."
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
  "created_at": "2026-02-22T03:27:03.946365Z",
  "response": "The capital of France is **Paris**.  \n\nIt's the political, cultural, and historical center of France, home to iconic landmarks like the Eiffel Tower, the Louvre Museum, and the Seine River. Paris has been the capital since the Middle Ages and is a symbol of French identity. \ud83c\uddeb\ud83c\uddf7",
  "done": true,
  "context": [],
  "total_duration": 0,
  "load_duration": 0,
  "prompt_eval_count": 17,
  "prompt_eval_duration": 0,
  "eval_count": 534,
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

**Endpoint:** `POST /v1/extract-book-metadata`

### Request Body

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAgAQADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigAoopksqQQvNIdqIpZjjOAOTQA+ivHvC/wAa9BfU9dXXPEGbc37DSx9if/j3/h+5Hn/vrmtJfGNroHxS8Xf29rbW2lwW9p5EU0rFFZkydic8nqdozQB6fRWJ4c8X6B4tglm0LU4rxYiBIFDKyZ6ZVgCAcHnHas/whJE+reJhH4huNVK6iweCWORRYnH+qUsSCB6rgUAdXRXFz/FrwJb37WUniO285W2kqjsmf98Lt/WuxiljnhSaJ1kjkUMjqchgeQQfSgB9Fcp4+kij0nTzN4huNDU6jABPBHI5mOTiIhCCA3qeOOa0/EPirQ/ClqlzrmpQ2cchITfks5HXaoBJxx0HegDYorA8OeNvDni0yroeqxXbxDc6BWR1HrtYA498Vv0AFFclrHxO8GaBqD2Gpa7BFdRtteNEeQofQ7FOD9a6LTdTsdZ0+K/026iurSUZSWJsqf8A6/tQBbori5/iz4FtrSG6l8QQrHMWVB5Mhf5SQSUC7gMgjJGDiuo0vVbDWtOh1DTbqK6tJhlJYzkHsfx9qALlFUNbKroGol7t7NRayk3KAloRtPzgDkkdeOeKw9G1vTNC+HFjq9/rst/p8FsjPqcsUm+YE4DlTl8kkepoA6uiuQk+KfgiLVF05/EVqLliFxhtgJ7F8bQfqeKk1P4l+DdH1c6Vf6/bRXitsZMMwQ+jMAVX8SMUAdXRWfquuaXoemHUtTvobazGP3zt8pz0x6k+1Y2hfEfwh4l1AWGk63BPdnO2JkeNmx127wN34ZoA6mis7W9e0rw5pzX+sX0Vnaqdu+Q9T6ADkn2FYNl8UPBeorbm012KU3F1HaRIIpA5lfO0FSuQDg/MQB70AdfRWVr3iXRfDFmt3rWow2cLHCmQnLn0VRkn8BVTw5438NeLWkXQ9Whu5IxueMBkcD12sAce+KAOgooooAKKKKACiiigAooooA86+Gf/ACMPj0d/7dk/lVTRdMs7z4/eK7y5t45ZrWztfJZ1B2FkXJGeh4xn6+tbepfDPTb7XrrWLPWNd0i5u2V7kaZe+SkzDjLDBrbsvDNlYeKtU8RRS3Bu9SjijmRmHlqIxgbRjI98k0AchHBFZftEuLaNYhd+HPNnCDAdxPjcffCgZpvw/tlvNW+Itq7MqzaxLGWU4IBXGR7812LeGbJvGaeKTLcfbksfsAj3DyvL3l84xndk+uMdqi03wfpumNr2x7iVdbnea6SRxgFhghdoBAwfUn3oA4WxtvFHw18KyWF14f0nXNBsUd5J7WXypjEMszPG4IYgZ4Br0rRNQs9V0Kwv9PXbZ3ECSQrt27UIBAx2wOMVxknwg0eZfs82u+JpdPPXT31NjAR6EYzj8a7y0tLews4LO1iWG3gjWOKNBgIoGAB+FAHAfGT/AJFzRf8AsOWn82q74x8KatqHiXSPEuhnT5b7TUki+y6iG8qRW7qVyVYc849PTne8S+GbLxVZWtpfS3EcdtdR3aGBgCXTOAcg8c1U8SeCLDxLeQ3sl/qun3kUflLcadeNC23JOD1B5J7UAZvhzxTJdeL5tD13w7HpOviz+0JJFKkyTw7sEhwAR838J9K7euX8M+AtJ8MX8+oxT39/qU6eXJfajcGaYpnO3PAAyB27V1FAHllj4g8WeKbrVZ/B2h+G7bTI7uS3e41TfvuXX7zFY/XjrTfgs1zE/i6xuPsSmDVmJjsN32dHIwwjzyFyvFbN38J9En1S7vbXUtb01LyQy3NpYXxigmY9Sy4zz7Gtnwp4J0jwZ/aC6QJkivZRK0TsGWPAwAvGcfUk+9AHIfA7SbCPwJJeC1iNxd3c4mkZAWcBioUn0wOnufWrXwiiS1j8YWMChLa28R3ccMY6Io2gAeg4rrvC3hmy8I6Iuk2EtxJAsjyBp2BbLNk8gAd/Sjw/4ZsvDcmqyWctw51O+kv5vOYHbI/ULgDC8cZyfegB/iv/AJE7XP8AsHz/APotq8v1T/k1hP8AsHwf+jUr17ULKPUtNurCZnWK5heFyhAYKwIOM9+awZ/AumXHgAeDXnuxpwhSHzQ6+dtVgw524zkelAHP+LtB0u0+Bt9ZQWUCQW+mCSNQg4dVBDf72ec9TSxaFpkXwFe2Wyh2SaCbh/kGWlMG8uT/AHt3Oa7LVdBtdX8NXGg3Eky2s9v9nZ4yA4XGMgkEZ/Cj+wbX/hFf+Ee8yb7J9i+w78jzNmzZnOMbse2M9qAPOoPE76T8K/BMEelw6tqmopBbWUNyQI1cLgOxPTAx781gfEH/AITW1XQNR8QxeFYPJ1W3+zPp3nfaVbOdoLcbcDkewr0y8+Heh3/g/T/DVz9qe208J9luBIFniZRgMGAAz+GPasiT4OaDciJ7/VNdv7qGVJIrq8vfNkQKc7VyuApIGeM8daAKnjCKC++M/gyy1NVewFvcSwRyDKPOB3B4JGFI98VW+LVlpyeJfAd55cSakdcgjVgAGeLepbPqAdv0z710PxNtvDU2g20viWG+FvHcDyryxRjLaPgnflQSo4x0IzjjpXmdhpmieKPGnh5PC9zrmufYr6O8vta1R5HEUURysSlwvU9senXsAbXiNPEF98d3i0uPQ5Lm10pHso9aEhjClvnaMJ/HnIz6A+la8HhLx3fePNE8Rav/AMItb/YGdZn0wzrLNGy4KtvBDY7ZIxk11/ijwTo3i0W8moJNFd2xJt7y1lMU0Wf7rD+RzVHRPh3YaNq8GqSaxr2qXdvu8ltSv2mEZZSpIXAHQkc0AdhRRRQAUUUUAf/Z"
          }
        }
      ]
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
  "result": {
    "title": "example",
    "author": "example",
    "subtitle": "example",
    "publisher": "example",
    "series_title": "example",
    "series_number": 0
  },
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
  "result": {
    "title": "This is an Image",
    "author": "The Author",
    "subtitle": "A Description of the Book",
    "publisher": "Example Publisher",
    "series_title": "Example Series",
    "series_number": 0
  },
  "usage": {
    "prompt_tokens": 163,
    "completion_tokens": 59,
    "total_tokens": 222
  }
}
```

---

## Test #38 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-book-metadata`

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
  "result": {
    "title": "example",
    "author": "example",
    "subtitle": "example",
    "publisher": "example",
    "series_title": "example",
    "series_number": 0
  },
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

**Endpoint:** `POST /v1/extract-book-metadata`

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
  "result": {
    "title": "example",
    "author": "example",
    "subtitle": "example",
    "publisher": "example",
    "series_title": "example",
    "series_number": 0
  },
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

**Endpoint:** `POST /v1/extract-book-metadata`

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

**Endpoint:** `POST /v1/extract-book-metadata`

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
  "result": {
    "title": "example",
    "author": "example",
    "subtitle": "example",
    "publisher": "example",
    "series_title": "example",
    "series_number": 0
  },
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

**Endpoint:** `POST /v1/extract-book-metadata`

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
  "result": {
    "title": "example",
    "author": "example",
    "subtitle": "example",
    "publisher": "example",
    "series_title": "example",
    "series_number": 0
  },
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

**Endpoint:** `POST /v1/extract-book-metadata`

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

**Endpoint:** `POST /v1/extract-book-metadata`

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
  "result": {
    "title": "example",
    "author": "example",
    "subtitle": "example",
    "publisher": "example",
    "series_title": "example",
    "series_number": 0
  },
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

**Endpoint:** `POST /v1/extract-book-metadata`

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
  "result": {
    "title": "example",
    "author": "example",
    "subtitle": "example",
    "publisher": "example",
    "series_title": "example",
    "series_number": 0
  },
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

**Endpoint:** `POST /v1/extract-book-metadata`

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

**Endpoint:** `POST /v1/extract-book-metadata`

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
  "result": {
    "title": "example",
    "author": "example",
    "subtitle": "example",
    "publisher": "example",
    "series_title": "example",
    "series_number": 0
  },
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

## Test #48 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-title`

### Request Body

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,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"
          }
        }
      ]
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
  "result": "this is an image",
  "usage": {
    "prompt_tokens": 90,
    "completion_tokens": 687,
    "total_tokens": 777
  }
}
```

---

## Test #49 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-book-title`

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

## Test #50 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-book-title`

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

## Test #51 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-book-title`

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

## Test #52 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-book-title`

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

## Test #53 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-book-title`

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

## Test #54 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-book-title`

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

## Test #55 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-book-title`

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

## Test #56 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-book-title`

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

## Test #57 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-book-title`

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

## Test #58 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-book-title`

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

## Test #59 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-nutrition-information`

### Request Body

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAgAQADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigAoopksqQQvNIdqIpZjjOAOTQA+ivHvC/wAa9BfU9dXXPEGbc37DSx9if/j3/h+5Hn/vrmtJfGNroHxS8Xf29rbW2lwW9p5EU0rFFZkydic8nqdozQB6fRWJ4c8X6B4tglm0LU4rxYiBIFDKyZ6ZVgCAcHnHas/whJE+reJhH4huNVK6iweCWORRYnH+qUsSCB6rgUAdXRXFz/FrwJb37WUniO285W2kqjsmf98Lt/WuxiljnhSaJ1kjkUMjqchgeQQfSgB9Fcp4+kij0nTzN4huNDU6jABPBHI5mOTiIhCCA3qeOOa0/EPirQ/ClqlzrmpQ2cchITfks5HXaoBJxx0HegDYorA8OeNvDni0yroeqxXbxDc6BWR1HrtYA498Vv0AFFclrHxO8GaBqD2Gpa7BFdRtteNEeQofQ7FOD9a6LTdTsdZ0+K/026iurSUZSWJsqf8A6/tQBbori5/iz4FtrSG6l8QQrHMWVB5Mhf5SQSUC7gMgjJGDiuo0vVbDWtOh1DTbqK6tJhlJYzkHsfx9qALlFUNbKroGol7t7NRayk3KAloRtPzgDkkdeOeKw9G1vTNC+HFjq9/rst/p8FsjPqcsUm+YE4DlTl8kkepoA6uiuQk+KfgiLVF05/EVqLliFxhtgJ7F8bQfqeKk1P4l+DdH1c6Vf6/bRXitsZMMwQ+jMAVX8SMUAdXRWfquuaXoemHUtTvobazGP3zt8pz0x6k+1Y2hfEfwh4l1AWGk63BPdnO2JkeNmx127wN34ZoA6mis7W9e0rw5pzX+sX0Vnaqdu+Q9T6ADkn2FYNl8UPBeorbm012KU3F1HaRIIpA5lfO0FSuQDg/MQB70AdfRWVr3iXRfDFmt3rWow2cLHCmQnLn0VRkn8BVTw5438NeLWkXQ9Whu5IxueMBkcD12sAce+KAOgooooAKKKKACiiigAooooA86+Gf/ACMPj0d/7dk/lVTRdMs7z4/eK7y5t45ZrWztfJZ1B2FkXJGeh4xn6+tbepfDPTb7XrrWLPWNd0i5u2V7kaZe+SkzDjLDBrbsvDNlYeKtU8RRS3Bu9SjijmRmHlqIxgbRjI98k0AchHBFZftEuLaNYhd+HPNnCDAdxPjcffCgZpvw/tlvNW+Itq7MqzaxLGWU4IBXGR7812LeGbJvGaeKTLcfbksfsAj3DyvL3l84xndk+uMdqi03wfpumNr2x7iVdbnea6SRxgFhghdoBAwfUn3oA4WxtvFHw18KyWF14f0nXNBsUd5J7WXypjEMszPG4IYgZ4Br0rRNQs9V0Kwv9PXbZ3ECSQrt27UIBAx2wOMVxknwg0eZfs82u+JpdPPXT31NjAR6EYzj8a7y0tLews4LO1iWG3gjWOKNBgIoGAB+FAHAfGT/AJFzRf8AsOWn82q74x8KatqHiXSPEuhnT5b7TUki+y6iG8qRW7qVyVYc849PTne8S+GbLxVZWtpfS3EcdtdR3aGBgCXTOAcg8c1U8SeCLDxLeQ3sl/qun3kUflLcadeNC23JOD1B5J7UAZvhzxTJdeL5tD13w7HpOviz+0JJFKkyTw7sEhwAR838J9K7euX8M+AtJ8MX8+oxT39/qU6eXJfajcGaYpnO3PAAyB27V1FAHllj4g8WeKbrVZ/B2h+G7bTI7uS3e41TfvuXX7zFY/XjrTfgs1zE/i6xuPsSmDVmJjsN32dHIwwjzyFyvFbN38J9En1S7vbXUtb01LyQy3NpYXxigmY9Sy4zz7Gtnwp4J0jwZ/aC6QJkivZRK0TsGWPAwAvGcfUk+9AHIfA7SbCPwJJeC1iNxd3c4mkZAWcBioUn0wOnufWrXwiiS1j8YWMChLa28R3ccMY6Io2gAeg4rrvC3hmy8I6Iuk2EtxJAsjyBp2BbLNk8gAd/Sjw/4ZsvDcmqyWctw51O+kv5vOYHbI/ULgDC8cZyfegB/iv/AJE7XP8AsHz/APotq8v1T/k1hP8AsHwf+jUr17ULKPUtNurCZnWK5heFyhAYKwIOM9+awZ/AumXHgAeDXnuxpwhSHzQ6+dtVgw524zkelAHP+LtB0u0+Bt9ZQWUCQW+mCSNQg4dVBDf72ec9TSxaFpkXwFe2Wyh2SaCbh/kGWlMG8uT/AHt3Oa7LVdBtdX8NXGg3Eky2s9v9nZ4yA4XGMgkEZ/Cj+wbX/hFf+Ee8yb7J9i+w78jzNmzZnOMbse2M9qAPOoPE76T8K/BMEelw6tqmopBbWUNyQI1cLgOxPTAx781gfEH/AITW1XQNR8QxeFYPJ1W3+zPp3nfaVbOdoLcbcDkewr0y8+Heh3/g/T/DVz9qe208J9luBIFniZRgMGAAz+GPasiT4OaDciJ7/VNdv7qGVJIrq8vfNkQKc7VyuApIGeM8daAKnjCKC++M/gyy1NVewFvcSwRyDKPOB3B4JGFI98VW+LVlpyeJfAd55cSakdcgjVgAGeLepbPqAdv0z710PxNtvDU2g20viWG+FvHcDyryxRjLaPgnflQSo4x0IzjjpXmdhpmieKPGnh5PC9zrmufYr6O8vta1R5HEUURysSlwvU9senXsAbXiNPEF98d3i0uPQ5Lm10pHso9aEhjClvnaMJ/HnIz6A+la8HhLx3fePNE8Rav/AMItb/YGdZn0wzrLNGy4KtvBDY7ZIxk11/ijwTo3i0W8moJNFd2xJt7y1lMU0Wf7rD+RzVHRPh3YaNq8GqSaxr2qXdvu8ltSv2mEZZSpIXAHQkc0AdhRRRQAUUUUAf/Z"
          }
        }
      ]
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
  "result": {
    "calories": 0,
    "serving_size": 0.0,
    "unit": "example"
  },
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
  "result": {
    "calories": 0,
    "serving_size": 0.0,
    "unit": "example"
  },
  "usage": {
    "prompt_tokens": 199,
    "completion_tokens": 26,
    "total_tokens": 225
  }
}
```

---

## Test #60 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-nutrition-information`

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
  "result": {
    "calories": 0,
    "serving_size": 0.0,
    "unit": "example"
  },
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

## Test #61 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-nutrition-information`

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
  "result": {
    "calories": 0,
    "serving_size": 0.0,
    "unit": "example"
  },
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

## Test #62 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-nutrition-information`

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

## Test #63 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-nutrition-information`

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
  "result": {
    "calories": 0,
    "serving_size": 0.0,
    "unit": "example"
  },
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

## Test #64 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-nutrition-information`

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
  "result": {
    "calories": 0,
    "serving_size": 0.0,
    "unit": "example"
  },
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

## Test #65 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-nutrition-information`

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

## Test #66 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-nutrition-information`

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
  "result": {
    "calories": 0,
    "serving_size": 0.0,
    "unit": "example"
  },
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

## Test #67 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-nutrition-information`

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
  "result": {
    "calories": 0,
    "serving_size": 0.0,
    "unit": "example"
  },
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

## Test #68 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-nutrition-information`

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

## Test #69 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/extract-nutrition-information`

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
  "result": {
    "calories": 0,
    "serving_size": 0.0,
    "unit": "example"
  },
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
