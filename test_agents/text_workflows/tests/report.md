# OpenAPI Contract Test Report

## Summary

- **Total Tests:** 61
- **Passed:** ✅ 61
- **Failed:** ❌ 0

---

## Test #1 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `GET /private/evaluate{path}/results`

### Expected Response

**Status:** `200 or 422`

```json
{
  "status": "idle",
  "workflow_path": "/v1/extract-nutrition-information"
}
```

### Actual Response

**Status:** `200`

```json
{
  "status": "idle",
  "workflow_path": "{path}",
  "current_evaluation": null,
  "results": null
}
```

---

## Test #2 ✅

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
  "available_providers": 2
}
```

---

## Test #3 ✅

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

## Test #4 ✅

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
  "status": "ready"
}
```

### Actual Response

**Status:** `200`

```json
{
  "available": [
    "default",
    "vision"
  ],
  "default": "default",
  "total": 11,
  "status": "ready"
}
```

---

## Test #5 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `GET /private/v1/workflows`

### Expected Response

**Status:** `200`

```json
{
  "total": 1,
  "workflows": [
    {
      "name": "nutrition_information_extraction",
      "path": "/v1/extract-nutrition-information",
      "description": "Takes an image of a packaged food product label and extracts the nutrition information as JSON.",
      "provider": "vision",
      "has_evaluation": true
    }
  ]
}
```

### Actual Response

**Status:** `200`

```json
{
  "total": 1,
  "workflows": [
    {
      "name": "summarize_text_small",
      "path": "/v1/summarize-text",
      "description": "Summarizes the given text into a concise summary.",
      "provider": null,
      "has_evaluation": false
    }
  ]
}
```

---

## Test #6 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /private/evaluate{path}`

### Expected Response

**Status:** `201 or 409 or 404 or 422`

```json
{
  "message": "Evaluation started for workflow: /v1/extract-nutrition-information",
  "workflow_path": "/v1/extract-nutrition-information"
}
```

### Actual Response

**Status:** `404`

```json
{
  "detail": "Workflow not found for path: 1"
}
```

---

## Test #7 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /private/cancel-evaluation`

### Request Body

```json
{
  "workflow_path": "/v1/extract-nutrition-information"
}
```

### Expected Response

**Status:** `200 or 404 or 422`

```json
{
  "message": "Evaluation cancelled for workflow: /v1/extract-nutrition-information",
  "workflow_path": "/v1/extract-nutrition-information"
}
```

### Actual Response

**Status:** `404`

```json
{
  "detail": "No running evaluation found for: /v1/extract-nutrition-information"
}
```

---

## Test #8 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /private/cancel-evaluation`

### Request Body

```json
{
  "workflow_path": "Lorem ipsum dolor sit amet"
}
```

### Expected Response

**Status:** `200 or 404 or 422`

```json
{
  "message": "Evaluation cancelled for workflow: /v1/extract-nutrition-information",
  "workflow_path": "/v1/extract-nutrition-information"
}
```

### Actual Response

**Status:** `404`

```json
{
  "detail": "No running evaluation found for: Lorem ipsum dolor sit amet"
}
```

---

## Test #9 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /private/cancel-evaluation`

### Request Body

```json
{
  "workflow_path": "Test with 'single' quotes"
}
```

### Expected Response

**Status:** `200 or 404 or 422`

```json
{
  "message": "Evaluation cancelled for workflow: /v1/extract-nutrition-information",
  "workflow_path": "/v1/extract-nutrition-information"
}
```

### Actual Response

**Status:** `404`

```json
{
  "detail": "No running evaluation found for: Test with 'single' quotes"
}
```

---

## Test #10 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /private/cancel-evaluation`

### Request Body

```json
{
  "workflow_path": "Test with \"double\" quotes"
}
```

### Expected Response

**Status:** `200 or 404 or 422`

```json
{
  "message": "Evaluation cancelled for workflow: /v1/extract-nutrition-information",
  "workflow_path": "/v1/extract-nutrition-information"
}
```

### Actual Response

**Status:** `404`

```json
{
  "detail": "No running evaluation found for: Test with \"double\" quotes"
}
```

---

## Test #11 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /private/cancel-evaluation`

### Request Body

```json
{
  "workflow_path": "Test:with:colons"
}
```

### Expected Response

**Status:** `200 or 404 or 422`

```json
{
  "message": "Evaluation cancelled for workflow: /v1/extract-nutrition-information",
  "workflow_path": "/v1/extract-nutrition-information"
}
```

### Actual Response

**Status:** `404`

```json
{
  "detail": "No running evaluation found for: Test:with:colons"
}
```

---

## Test #12 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /private/cancel-evaluation`

### Request Body

```json
{
  "workflow_path": "Test\\with\\backslashes"
}
```

### Expected Response

**Status:** `200 or 404 or 422`

```json
{
  "message": "Evaluation cancelled for workflow: /v1/extract-nutrition-information",
  "workflow_path": "/v1/extract-nutrition-information"
}
```

### Actual Response

**Status:** `404`

```json
{
  "detail": "No running evaluation found for: Test\\with\\backslashes"
}
```

---

## Test #13 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /private/cancel-evaluation`

### Request Body

```json
{
  "workflow_path": "Test\nwith\nnewlines"
}
```

### Expected Response

**Status:** `200 or 404 or 422`

```json
{
  "message": "Evaluation cancelled for workflow: /v1/extract-nutrition-information",
  "workflow_path": "/v1/extract-nutrition-information"
}
```

### Actual Response

**Status:** `404`

```json
{
  "detail": "No running evaluation found for: Test\nwith\nnewlines"
}
```

---

## Test #14 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /private/cancel-evaluation`

### Request Body

```json
{
  "workflow_path": "Test\r\nwith\r\nCRLF"
}
```

### Expected Response

**Status:** `200 or 404 or 422`

```json
{
  "message": "Evaluation cancelled for workflow: /v1/extract-nutrition-information",
  "workflow_path": "/v1/extract-nutrition-information"
}
```

### Actual Response

**Status:** `404`

```json
{
  "detail": "No running evaluation found for: Test\r\nwith\r\nCRLF"
}
```

---

## Test #15 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /private/cancel-evaluation`

### Request Body

```json
{
  "workflow_path": "Test with UTF-8: caf\u00e9, na\u00efve, \u4e2d\u6587, \u65e5\u672c\u8a9e"
}
```

### Expected Response

**Status:** `200 or 404 or 422`

```json
{
  "message": "Evaluation cancelled for workflow: /v1/extract-nutrition-information",
  "workflow_path": "/v1/extract-nutrition-information"
}
```

### Actual Response

**Status:** `404`

```json
{
  "detail": "No running evaluation found for: Test with UTF-8: caf\u00e9, na\u00efve, \u4e2d\u6587, \u65e5\u672c\u8a9e"
}
```

---

## Test #16 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /private/cancel-evaluation`

### Request Body

```json
{
  "workflow_path": "Test!@#$%^&*()_+-=[]{}|;:<>?,./`~"
}
```

### Expected Response

**Status:** `200 or 404 or 422`

```json
{
  "message": "Evaluation cancelled for workflow: /v1/extract-nutrition-information",
  "workflow_path": "/v1/extract-nutrition-information"
}
```

### Actual Response

**Status:** `404`

```json
{
  "detail": "No running evaluation found for: Test!@#$%^&*()_+-=[]{}|;:<>?,./`~"
}
```

---

## Test #17 ✅

🔧 *Test case generated from schema*

**Endpoint:** `POST /private/cancel-evaluation`

### Request Body

```json
{
  "workflow_path": ""
}
```

### Expected Response

**Status:** `200 or 404 or 422`

```json
{
  "message": "Evaluation cancelled for workflow: /v1/extract-nutrition-information",
  "workflow_path": "/v1/extract-nutrition-information"
}
```

### Actual Response

**Status:** `422`

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "workflow_path"
      ],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Test #18 ✅

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
  "message": "Okay! The weather in Reykjavik, Iceland is cold and cloudy with a temperature of 5\u00b0C (41\u00b0F) and a wind of 15 km/h.",
  "role": "assistant",
  "created": 1772687425,
  "usage": {
    "prompt_tokens": 3828,
    "completion_tokens": 38,
    "total_tokens": 3866
  }
}
```

---

## Test #19 ✅

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

## Test #20 ✅

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

## Test #21 ✅

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

## Test #22 ✅

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

## Test #23 ✅

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

## Test #24 ✅

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

## Test #25 ✅

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

## Test #26 ✅

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

## Test #27 ✅

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

## Test #28 ✅

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

## Test #29 ✅

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
  "id": "chatcmpl-2db5ee766a5149549e734c84",
  "object": "chat.completion",
  "created": 1772687560,
  "model": "ollama/gemma3:1b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "###The capital of France is Paris. \ud83d\ude0a \n\nWould you like to know more about Paris or perhaps something else?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 21,
    "completion_tokens": 24,
    "total_tokens": 45
  }
}
```

---

## Test #30 ✅

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

## Test #31 ✅

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

## Test #32 ✅

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

## Test #33 ✅

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
  "id": "chatcmpl-3599239ac63347489f135e3e",
  "object": "chat.completion",
  "created": 1772687573,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the standard \"Lorem ipsum\" placeholder text. \n\nIs there anything I can do with this text? For example, would you like me to:\n\n*   **Analyze it?** (e.g., count words, identify patterns?)\n*   **Generate variations?** (e.g., rewrite it, change the font?)\n*   **Translate it?**\n*   **Do something else related to it?**"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 99,
    "total_tokens": 118
  }
}
```

---

## Test #34 ✅

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
  "id": "chatcmpl-c2d758b869f541308a718783",
  "object": "chat.completion",
  "created": 1772687577,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic \"Lorem ipsum\" placeholder text. \n\nIs there anything I can help you with regarding it? For example, would you like me to:\n\n*   **Explain what it is?** (It's a placeholder text used in printing and design to simulate the appearance of text without needing actual content.)\n*   **Provide examples of its usage?**\n*   **Generate variations or alternative text?**\n*   **Or something else entirely?**"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 106,
    "total_tokens": 125
  }
}
```

---

## Test #35 ✅

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

## Test #36 ✅

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

## Test #37 ✅

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

## Test #38 ✅

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

## Test #39 ✅

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

## Test #40 ✅

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
  "created_at": "2026-03-05T05:12:59.586262Z",
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

## Test #41 ✅

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

## Test #42 ✅

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

## Test #43 ✅

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

## Test #44 ✅

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

## Test #45 ✅

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

## Test #46 ✅

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

## Test #47 ✅

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

## Test #48 ✅

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

## Test #49 ✅

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

## Test #50 ✅

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

## Test #51 ✅

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
  "result": "Please provide the user message you\u2019d like me to clean up and summarize.",
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 17,
    "total_tokens": 67
  }
}
```

---

## Test #52 ✅

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

## Test #53 ✅

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

## Test #54 ✅

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

## Test #55 ✅

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

## Test #56 ✅

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

## Test #57 ✅

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

## Test #58 ✅

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

## Test #59 ✅

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

## Test #60 ✅

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

## Test #61 ✅

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
