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
  "stream": false
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503 or 408`

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
  "message": "I need to know your location to check the weather! \ud83d\ude0a Could you please tell me where you are? \ud83c\udf24\ufe0f",
  "role": "assistant",
  "created": 1770601988,
  "usage": {
    "prompt_tokens": 802,
    "completion_tokens": 1635,
    "total_tokens": 2437
  }
}
```

---

## Test #5 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "timeout": 0.0,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503 or 408`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #6 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "timeout": 0.0,
  "max_tokens": 500000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503 or 408`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #7 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "timeout": 0.0,
  "max_tokens": 1000000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503 or 408`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #8 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "timeout": 0.123456789,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503 or 408`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #9 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "timeout": 0.123456789,
  "max_tokens": 500000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503 or 408`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #10 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "timeout": 0.123456789,
  "max_tokens": 1000000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503 or 408`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #11 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "timeout": 0.999999999,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503 or 408`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #12 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "timeout": 0.999999999,
  "max_tokens": 500000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503 or 408`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #13 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "timeout": 0.999999999,
  "max_tokens": 1000000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503 or 408`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
```

---

## Test #14 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": true,
  "timeout": 1.111111111,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503 or 408`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
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
  ]
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
  "id": "chatcmpl-b377847f598c42f185bcbe32",
  "object": "chat.completion",
  "created": 1770601996,
  "model": "qwen3-vl:2b-q4km",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of **France** is **Paris**.  \n\n### Key details about Paris:\n- **Historical Significance**: Founded as a Roman settlement, it has been the political, cultural, and economic heart of France for over 2,000 years.\n- **Iconic Symbols**: The Eiffel Tower (built for the 1889 World's Fair), the Seine River, and the Louvre Museum are landmarks that define its identity.\n- **Cultural Hub**: Home to major institutions like the Mus\u00e9e d\u2019Orsay, the Centre Pompidou, and the Place de la Concorde.\n- **Geographical Note**: Located on the Seine River in northern France, it\u2019s known for its vibrant arts scene, fashion industry, and iconic architecture.\n\nParis remains the **undisputed capital** of France, with its history and culture making it a global symbol of European heritage. \ud83c\uddeb\ud83c\uddf7"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 17,
    "completion_tokens": 569,
    "total_tokens": 586
  }
}
```

---

## Test #16 ✅

📋 *Test case from OpenAPI example*

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
  "timeout": 0.0
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
  "id": "chatcmpl-82d26779fadc4a1db2c9edb4",
  "object": "chat.completion",
  "created": 1770602000,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! It seems like you've used \"Lorem ipsum dolor sit amet\" \u2014 a common placeholder text often used in design and layout contexts. I'm here to help! Could you tell me what you need assistance with? \ud83d\ude0a"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 397,
    "total_tokens": 412
  }
}
```

---

## Test #17 ✅

📋 *Test case from OpenAPI example*

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
  "timeout": 0.123456789
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

## Test #18 ✅

📋 *Test case from OpenAPI example*

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
  "timeout": 0.999999999
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

## Test #19 ✅

📋 *Test case from OpenAPI example*

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
  "timeout": 1.111111111
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

## Test #20 ✅

📋 *Test case from OpenAPI example*

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
  "timeout": 500000.0
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
  "id": "chatcmpl-0ac41c01babc4c56a9fdbe40",
  "object": "chat.completion",
  "created": 1770602014,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "I notice you've shared placeholder text (\"Lorem ipsum dolor sit amet\"). This is commonly used in design or content creation to represent generic content. How can I assist you today? Whether you need help with writing, problem-solving, or anything else, feel free to ask! \ud83d\ude0a"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 282,
    "total_tokens": 297
  }
}
```

---

## Test #21 ✅

📋 *Test case from OpenAPI example*

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
  "timeout": 1000000.0
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
  "id": "chatcmpl-c4ff806fe6a84d109611cd0a",
  "object": "chat.completion",
  "created": 1770602017,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Ah, I see! You've shared some placeholder text: *\"Lorem ipsum dolor sit amet.\"* \ud83d\ude04 This is commonly used in design and publishing to create mockups or layouts without specific content. It's meant to be filler text\u2014often used for visual design, not for actual messaging.\n\nIf you're asking about it or need help with something else (like writing a story, designing a layout, or clarifying a question), feel free to ask! I'm here to assist. \ud83d\ude0a"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 268,
    "total_tokens": 283
  }
}
```

---

## Test #22 ✅

📋 *Test case from OpenAPI example*

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
  "timeout": 0.0
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
  "id": "chatcmpl-6da491e4f9c643d1840ad799",
  "object": "chat.completion",
  "created": 1770602034,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! I see you've used \"Lorem ipsum\" \u2014 a common placeholder text used in design and publishing to fill space before actual content. It's often used to test layouts or as a default text. How can I assist you today? \ud83d\ude0a"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 1628,
    "total_tokens": 1643
  }
}
```

---

## Test #23 ✅

📋 *Test case from OpenAPI example*

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
  "timeout": 0.123456789
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

## Test #24 ✅

📋 *Test case from OpenAPI example*

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
  "timeout": 0.999999999
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

## Test #25 ✅

📋 *Test case from OpenAPI example*

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
  "timeout": 1.111111111
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
  "created_at": "2026-02-09T01:54:11.559883Z",
  "response": "The capital of France is **Paris**.  \n\n### Key Details:\n- **Location**: Situated in the \u00cele-de-France region, near the Seine River.\n- **Significance**:  \n  - Hosts the **French government** (Chancellery, National Assembly, and President's residence).  \n  - Home to iconic landmarks like the **Eiffel Tower**, **Louvre Museum**, and **Seine River**.  \n  - A global cultural and historical hub (birthplace of the Renaissance, home to the Louvre, and the city's vibrant arts scene).  \n- **Historical Note**: Paris was founded in 1180 and became the capital in 1870 after the Franco-Prussian War.  \n\nIf you're curious about why it matters or have follow-up questions (e.g., \"What's the city's nickname?\"), feel free to ask! \ud83d\ude0a",
  "done": true,
  "context": [],
  "total_duration": 0,
  "load_duration": 0,
  "prompt_eval_count": 17,
  "prompt_eval_duration": 0,
  "eval_count": 492,
  "eval_duration": 0
}
```

---

## Test #27 ✅

📋 *Test case from OpenAPI example*

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

📋 *Test case from OpenAPI example*

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

📋 *Test case from OpenAPI example*

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

📋 *Test case from OpenAPI example*

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

📋 *Test case from OpenAPI example*

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

📋 *Test case from OpenAPI example*

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

📋 *Test case from OpenAPI example*

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

📋 *Test case from OpenAPI example*

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

📋 *Test case from OpenAPI example*

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

📋 *Test case from OpenAPI example*

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
            "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAgAQADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigAooooAKKKKACiiigAooooAKKKo3+sWOmXWn213cJFLfz/Z7cMwG59rNj/x3H1IHegC9RWJp3izR9U0Yana3kDILVbuWEzxiSBGXd+8G7CYHXJxwea0YdSsrm5ntre7t57m3/wBbDHKrPH7MM8fjQBaoqhaa1pt7LFDBf2r3EsKzrCs6M5jIBDYUnIwRyMj3o/tvSTFPKNUsvLt5BFM/2hMROTgKxzwSSBg96AL9FURq9hJpcupW95b3FnErM00UyFAF+9ls7Rjvk8Uy58QaLZ3E1vdavYQTQjMsctyisgwDlgTkcMp59R60AaNFVBqmntdpaLf2puZI/NSETLvZP7wXOSPfpUEfiHRJoJp4tY094oApmkW5QrGGJC7jnjJBAz1waANKio4J4bqBJ7eVJYZBuSSNgysPUEdRUlABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAVlavp9zeXui3Fv5X+g33nyLIxXchhliOMA8jzM474xkda1aKAOEfwRejwtY6XE9mksHhq50lyGYKZ5VhAYfLnbmNyTjPI45Na2j6Hf6f4iu7t/sqWMnnFUjdnYvJKH3AMuY++4BirMd2FxiulooA4jw34S1XRbrSd7WIhtreFLlo5GbzXS2WHIRlwrZUfvFZcoNpXvVWz8E6sYblL97F/O/swMElZkcW1y0sh27AEDK2AgyAeM969BooA5m+8O3dzo/jCzjkgD615n2YknCbrWOH5+OPmRjxngjvxTG8Lzv4iOot9maM6yL/ByW8v7B9nx0+9v5x0xznPFdTRQB5g/gLXBplnazT2xitbMRM9tKwkyLB7YhU2gO29twdmBxgcY5lg0bVvEWqz6m1ill5K2QjhWS4tFmMa3Ksu/Ysi4E6kEKR8oHODXpVFAGZoGmtpGjQ2bhBIGkkcI7uAzuzn5nJZuWPJ69cDpWnRRQAUUUUAFFFFABRRRQAUUUUAFFFFAH/9k="
          }
        }
      ]
    }
  ],
  "temperature": 0.7,
  "max_tokens": 4096
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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
    "title": "This Is Not an Image",
    "author": "A. Smith",
    "subtitle": "A New Look at the World",
    "publisher": "Penguin Books",
    "series_title": "The World's Books",
    "series_number": 1
  },
  "usage": {
    "prompt_tokens": 163,
    "completion_tokens": 55,
    "total_tokens": 218
  }
}
```

---

## Test #38 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-metadata`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-metadata`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 500000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-metadata`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 1000000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

## Test #41 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-metadata`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.123456789,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-metadata`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.123456789,
  "max_tokens": 500000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-metadata`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.123456789,
  "max_tokens": 1000000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

## Test #44 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-metadata`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.999999999,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-metadata`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.999999999,
  "max_tokens": 500000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-metadata`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.999999999,
  "max_tokens": 1000000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

## Test #47 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-metadata`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 1.0,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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
            "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAgAQADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigAooooAKKKKACiiigAooooAKKKo3+sWOmXWn213cJFLfz/Z7cMwG59rNj/x3H1IHegC9RWJp3izR9U0Yana3kDILVbuWEzxiSBGXd+8G7CYHXJxwea0YdSsrm5ntre7t57m3/wBbDHKrPH7MM8fjQBaoqhaa1pt7LFDBf2r3EsKzrCs6M5jIBDYUnIwRyMj3o/tvSTFPKNUsvLt5BFM/2hMROTgKxzwSSBg96AL9FURq9hJpcupW95b3FnErM00UyFAF+9ls7Rjvk8Uy58QaLZ3E1vdavYQTQjMsctyisgwDlgTkcMp59R60AaNFVBqmntdpaLf2puZI/NSETLvZP7wXOSPfpUEfiHRJoJp4tY094oApmkW5QrGGJC7jnjJBAz1waANKio4J4bqBJ7eVJYZBuSSNgysPUEdRUlABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAVlavp9zeXui3Fv5X+g33nyLIxXchhliOMA8jzM474xkda1aKAOEfwRejwtY6XE9mksHhq50lyGYKZ5VhAYfLnbmNyTjPI45Na2j6Hf6f4iu7t/sqWMnnFUjdnYvJKH3AMuY++4BirMd2FxiulooA4jw34S1XRbrSd7WIhtreFLlo5GbzXS2WHIRlwrZUfvFZcoNpXvVWz8E6sYblL97F/O/swMElZkcW1y0sh27AEDK2AgyAeM969BooA5m+8O3dzo/jCzjkgD615n2YknCbrWOH5+OPmRjxngjvxTG8Lzv4iOot9maM6yL/ByW8v7B9nx0+9v5x0xznPFdTRQB5g/gLXBplnazT2xitbMRM9tKwkyLB7YhU2gO29twdmBxgcY5lg0bVvEWqz6m1ill5K2QjhWS4tFmMa3Ksu/Ysi4E6kEKR8oHODXpVFAGZoGmtpGjQ2bhBIGkkcI7uAzuzn5nJZuWPJ69cDpWnRRQAUUUUAFFFFABRRRQAUUUUAFFFFAH/9k="
          }
        }
      ]
    }
  ],
  "temperature": 0.7,
  "max_tokens": 4096
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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
  "result": "this is not a magic",
  "usage": {
    "prompt_tokens": 90,
    "completion_tokens": 121,
    "total_tokens": 211
  }
}
```

---

## Test #49 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-title`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-title`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 500000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-title`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 1000000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

## Test #52 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-title`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.123456789,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-title`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.123456789,
  "max_tokens": 500000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-title`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.123456789,
  "max_tokens": 1000000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

## Test #55 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-title`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.999999999,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-title`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.999999999,
  "max_tokens": 500000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-title`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.999999999,
  "max_tokens": 1000000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

## Test #58 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-book-title`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 1.0,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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
            "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAgAQADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigAooooAKKKKACiiigAooooAKKKo3+sWOmXWn213cJFLfz/Z7cMwG59rNj/x3H1IHegC9RWJp3izR9U0Yana3kDILVbuWEzxiSBGXd+8G7CYHXJxwea0YdSsrm5ntre7t57m3/wBbDHKrPH7MM8fjQBaoqhaa1pt7LFDBf2r3EsKzrCs6M5jIBDYUnIwRyMj3o/tvSTFPKNUsvLt5BFM/2hMROTgKxzwSSBg96AL9FURq9hJpcupW95b3FnErM00UyFAF+9ls7Rjvk8Uy58QaLZ3E1vdavYQTQjMsctyisgwDlgTkcMp59R60AaNFVBqmntdpaLf2puZI/NSETLvZP7wXOSPfpUEfiHRJoJp4tY094oApmkW5QrGGJC7jnjJBAz1waANKio4J4bqBJ7eVJYZBuSSNgysPUEdRUlABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAVlavp9zeXui3Fv5X+g33nyLIxXchhliOMA8jzM474xkda1aKAOEfwRejwtY6XE9mksHhq50lyGYKZ5VhAYfLnbmNyTjPI45Na2j6Hf6f4iu7t/sqWMnnFUjdnYvJKH3AMuY++4BirMd2FxiulooA4jw34S1XRbrSd7WIhtreFLlo5GbzXS2WHIRlwrZUfvFZcoNpXvVWz8E6sYblL97F/O/swMElZkcW1y0sh27AEDK2AgyAeM969BooA5m+8O3dzo/jCzjkgD615n2YknCbrWOH5+OPmRjxngjvxTG8Lzv4iOot9maM6yL/ByW8v7B9nx0+9v5x0xznPFdTRQB5g/gLXBplnazT2xitbMRM9tKwkyLB7YhU2gO29twdmBxgcY5lg0bVvEWqz6m1ill5K2QjhWS4tFmMa3Ksu/Ysi4E6kEKR8oHODXpVFAGZoGmtpGjQ2bhBIGkkcI7uAzuzn5nJZuWPJ69cDpWnRRQAUUUUAFFFFABRRRQAUUUUAFFFFAH/9k="
          }
        }
      ]
    }
  ],
  "temperature": 0.7,
  "max_tokens": 4096
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-nutrition-information`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-nutrition-information`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 500000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-nutrition-information`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.0,
  "max_tokens": 1000000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

## Test #63 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-nutrition-information`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.123456789,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-nutrition-information`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.123456789,
  "max_tokens": 500000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-nutrition-information`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.123456789,
  "max_tokens": 1000000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

## Test #66 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-nutrition-information`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.999999999,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-nutrition-information`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.999999999,
  "max_tokens": 500000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-nutrition-information`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 0.999999999,
  "max_tokens": 1000000
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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

## Test #69 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/extract-nutrition-information`

### Request Body

```json
{
  "messages": [],
  "model": "Lorem ipsum dolor sit amet",
  "temperature": 1.0,
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200 or 501 or 429 or 422`

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
