# OpenAPI Contract Test Report

## Summary

- **Total Tests:** 84
- **Passed:** ✅ 84
- **Failed:** ❌ 0

---

## Test #1 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `GET /private/v1/books`

### Expected Response

**Status:** `200`

```json
[
  {
    "file_path": "shelf1/simple-psionics.pdf",
    "tags": [
      "shelf1"
    ],
    "chunk_count": 51
  },
  {
    "file_path": "shelf2/FashionDesigner.pdf",
    "tags": [
      "shelf2"
    ],
    "chunk_count": 5
  }
]
```

### Actual Response

**Status:** `200`

```json
[
  {
    "file_path": "shelf1/simple-psionics.pdf",
    "tags": [
      "shelf1"
    ],
    "chunk_count": 51
  },
  {
    "file_path": "shelf2/FashionDesigner.pdf",
    "tags": [
      "shelf2"
    ],
    "chunk_count": 5
  },
  {
    "file_path": "shelf2/lycanthropes-in-eberron.pdf",
    "tags": [
      "shelf2"
    ],
    "chunk_count": 10
  }
]
```

---

## Test #2 ✅

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

## Test #3 ✅

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

## Test #4 ✅

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

## Test #5 ✅

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
    "vision"
  ],
  "default": "vision",
  "total": 10,
  "status": "ready"
}
```

---

## Test #6 ✅

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
  "total": 3,
  "workflows": [
    {
      "name": "book_metadata_extraction",
      "path": "/v1/extract-book-metadata",
      "description": "Takes an image of a book cover and extracts the book metadata as JSON.",
      "provider": "vision",
      "has_evaluation": false
    },
    {
      "name": "book_title_extraction",
      "path": "/v1/extract-book-title",
      "description": "Takes an image of a book cover and extracts the book title as a string.",
      "provider": "vision",
      "has_evaluation": false
    },
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

---

## Test #7 ✅

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

## Test #8 ✅

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

## Test #9 ✅

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

## Test #10 ✅

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

## Test #11 ✅

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

## Test #12 ✅

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

## Test #13 ✅

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

## Test #14 ✅

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

## Test #15 ✅

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

## Test #16 ✅

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

## Test #17 ✅

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

## Test #18 ✅

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

## Test #19 ✅

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
  "message": "Okay! The weather in Reykjavik, Iceland is cold and cloudy with a temperature of 5\u00b0C (41\u00b0F) and a wind of 15 km/h. \ud83d\ude0a",
  "role": "assistant",
  "created": 1773582943,
  "usage": {
    "prompt_tokens": 2594,
    "completion_tokens": 1163,
    "total_tokens": 3757
  }
}
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

## Test #29 ✅

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

## Test #30 ✅

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
  "id": "chatcmpl-6e97b728b67b4c4d985eebcd",
  "object": "chat.completion",
  "created": 1773583005,
  "model": "qwen3-vl:2b-q4km",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is **Paris**.  \n\n### Key Details:\n- **Location**: Situated in the \u00cele-de-France region, near the Seine River.\n- **Role**: Official seat of the French government, including the National Assembly, the Presidential Palace, and the Chancellery.\n- **Historical Significance**: Became the capital in the 15th century after the fall of the Middle Ages, with its status solidified during the French Revolution (1792\u20131799) and the Bourbon Restoration (1815).  \n- **Population**: Approximately 2.1 million (as of 2023), making it one of Europe\u2019s most populous cities.  \n\nParis is renowned for its iconic landmarks (like the Eiffel Tower), cultural diversity, and as a global hub for arts, fashion, and science. \ud83c\uddeb\ud83c\uddf7"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 17,
    "completion_tokens": 666,
    "total_tokens": 683
  }
}
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
  "id": "chatcmpl-f6b0372e26c8407e9083ee47",
  "object": "chat.completion",
  "created": 1773583019,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! I notice you've shared some placeholder text\u2014*Lorem ipsum dolor sit amet*\u2014which is commonly used in design and publishing to create space. \ud83d\ude0a This phrase is often used as filler text to demonstrate layouts without specific content.  \n\nIf you'd like to discuss something related to design, writing, or another topic, feel free to ask! What would you like to explore? \ud83c\udf1f"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 361,
    "total_tokens": 376
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
  "id": "chatcmpl-265df4f3fcd64359ac103b7e",
  "object": "chat.completion",
  "created": 1773583021,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! I see you've sent some placeholder text\u2014*Lorem ipsum*\u2014which is often used in design or publishing to fill space. \ud83d\ude0a Would you like help with something specific? Whether it's crafting a message, brainstorming ideas, or just chatting, I'm here to assist! What would you like to do today? \ud83c\udf1f"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 162,
    "total_tokens": 177
  }
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

## Test #40 ✅

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

## Test #41 ✅

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
  "created_at": "2026-03-15T13:57:12.699684Z",
  "response": "The capital of France is **Paris**.  \n\nIt has been the capital since the Middle Ages and is renowned for landmarks like the Eiffel Tower, the Louvre Museum, and its vibrant culture. Paris is also the largest city in France and a global hub for art, fashion, and history. \ud83c\uddeb\ud83c\uddf7",
  "done": true,
  "context": [],
  "total_duration": 0,
  "load_duration": 0,
  "prompt_eval_count": 17,
  "prompt_eval_duration": 0,
  "eval_count": 421,
  "eval_duration": 0
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

## Test #51 ✅

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

## Test #52 ✅

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
    "title": "This is an image",
    "author": "example",
    "subtitle": "example",
    "publisher": "example",
    "series_title": "example",
    "series_number": 0
  },
  "usage": {
    "prompt_tokens": 163,
    "completion_tokens": 52,
    "total_tokens": 215
  }
}
```

---

## Test #53 ✅

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

## Test #54 ✅

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

## Test #55 ✅

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

## Test #56 ✅

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

## Test #57 ✅

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

## Test #58 ✅

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

## Test #59 ✅

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

## Test #60 ✅

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

## Test #61 ✅

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

## Test #62 ✅

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

## Test #63 ✅

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
  "result": "",
  "usage": {
    "prompt_tokens": 90,
    "completion_tokens": 4006,
    "total_tokens": 4096
  }
}
```

---

## Test #64 ✅

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

## Test #65 ✅

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

## Test #66 ✅

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

## Test #67 ✅

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

## Test #68 ✅

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

## Test #69 ✅

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

## Test #70 ✅

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

## Test #71 ✅

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

## Test #72 ✅

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

## Test #73 ✅

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

## Test #74 ✅

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
    "prompt_tokens": 198,
    "completion_tokens": 24,
    "total_tokens": 222
  }
}
```

---

## Test #75 ✅

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

## Test #76 ✅

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

## Test #77 ✅

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

## Test #78 ✅

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

## Test #79 ✅

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

## Test #80 ✅

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

## Test #81 ✅

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

## Test #82 ✅

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

## Test #83 ✅

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

## Test #84 ✅

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
