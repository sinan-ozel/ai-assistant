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
  "providers_loading": false
}
```

### Actual Response

**Status:** `200`

```json
{
  "status": "ok",
  "providers_loading": false
}
```

---

## Test #2 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `GET /private/v1/providers/{provider}/max-context-window`

### Expected Response

**Status:** `200`

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
  "stream": false
}
```

### Expected Response

**Status:** `200`

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
  "message": "Okay, let\u2019s check the weather for **London, England**. \n\nHere\u2019s the forecast:\n\nCurrently, London is experiencing light rain with a temperature of 15\u00b0C (59\u00b0F). It's expected to continue with a high of 18\u00b0C (64\u00b0F) later today.",
  "role": "assistant",
  "created": 1769830780,
  "usage": {
    "prompt_tokens": 682,
    "completion_tokens": 70,
    "total_tokens": 752
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
  "stream": true
}
```

### Expected Response

**Status:** `200`

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

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "stream": false
}
```

### Expected Response

**Status:** `200`

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
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Lorem ipsum dolor sit amet",
  "message": "That\u2019s a really good explanation! Thanks. Do you have any more information about its history or purpose?",
  "role": "assistant",
  "created": 1769830785,
  "usage": {
    "prompt_tokens": 315,
    "completion_tokens": 23,
    "total_tokens": 338
  }
}
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
  "user_id": "Test with 'single' quotes",
  "stream": true
}
```

### Expected Response

**Status:** `200`

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

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Test with 'single' quotes",
  "stream": false
}
```

### Expected Response

**Status:** `200`

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
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Test with 'single' quotes",
  "message": "Okay! Let\u2019s delve deeper into the history. It\u2019s a great example of how a seemingly simple placeholder can have surprisingly significant origins.\n\nSo, you\u2019re asking about how the Lorem Ipsum text evolved from its initial purpose as a testing tool for typography? It started as a way for the type founders to test how different fonts and layouts looked together. They\u2019d create a massive block of text \u2013 hundreds of pages \u2013 and use it to see what the overall look and feel of a book\u2019s text would be. They\u2019d then drastically reduce the text to just a few lines, effectively creating a placeholder that didn\u2019t contain any actual content.\n\nEssentially, it was a way to quickly assess the visual impact of typography without the cost and time of actually writing the text. It was a brilliant, pragmatic solution for their testing process!\n\nDo you want to hear about a specific example of how it was used in a test, or perhaps how the text evolved over time?",
  "role": "assistant",
  "created": 1769830797,
  "usage": {
    "prompt_tokens": 515,
    "completion_tokens": 201,
    "total_tokens": 716
  }
}
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
  "user_id": "Test with \"double\" quotes",
  "stream": true
}
```

### Expected Response

**Status:** `200`

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

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Test with \"double\" quotes",
  "stream": false
}
```

### Expected Response

**Status:** `200`

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
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Test with \"double\" quotes",
  "message": "Okay, I understand. You\u2019ve provided the placeholder text again. It\u2019s a common placeholder! \ud83d\ude0a\n\nLet's just acknowledge that you've provided the placeholder text. It\u2019s a very common placeholder! \ud83d\ude0a\n\nIs there anything specific you\u2019d like to do with it, or are you just acknowledging its presence?",
  "role": "assistant",
  "created": 1769830804,
  "usage": {
    "prompt_tokens": 644,
    "completion_tokens": 69,
    "total_tokens": 713
  }
}
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
  "user_id": "Test:with:colons",
  "stream": true
}
```

### Expected Response

**Status:** `200`

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

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Test:with:colons",
  "stream": false
}
```

### Expected Response

**Status:** `200`

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
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Test:with:colons",
  "message": "Okay, you\u2019ve provided the input \u2013 \u201cLorem ipsum dolor sit amet\u201d. How can I assist you today?",
  "role": "assistant",
  "created": 1769830811,
  "usage": {
    "prompt_tokens": 664,
    "completion_tokens": 24,
    "total_tokens": 688
  }
}
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
  "user_id": "Test\\with\\backslashes",
  "stream": true
}
```

### Expected Response

**Status:** `200`

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

🔧 *Test case generated from schema*

**Endpoint:** `POST /v1/agent/chat`

### Request Body

```json
{
  "message": "Lorem ipsum dolor sit amet",
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Test\\with\\backslashes",
  "stream": false
}
```

### Expected Response

**Status:** `200`

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
  "conversation_id": "Lorem ipsum dolor sit amet",
  "user_id": "Test\\with\\backslashes",
  "message": "That\u2019s right! It\u2019s a placeholder text. \ud83d\ude0a",
  "role": "assistant",
  "created": 1769830818,
  "usage": {
    "prompt_tokens": 597,
    "completion_tokens": 14,
    "total_tokens": 611
  }
}
```

---

## Test #15 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/chat/completions`

### Request Body

```json
{
  "model": "pixtral",
  "messages": [
    {
      "role": "user",
      "content": "What is the capital of France?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 100
}
```

### Expected Response

**Status:** `200`

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
  "id": "chatcmpl-c3e481843b924d999715b3e6",
  "object": "chat.completion",
  "created": 1769830820,
  "model": "pixtral",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is **Paris**. \n\nIt\u2019s a great question! \ud83d\ude0a"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 21,
    "completion_tokens": 19,
    "total_tokens": 40
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
  "temperature": 0.0,
  "max_tokens": 1,
  "stream": true,
  "top_p": 0.0,
  "stop": []
}
```

### Expected Response

**Status:** `200`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
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
  "temperature": 0.0,
  "max_tokens": 1,
  "stream": true,
  "top_p": 0.0,
  "stop": [
    "Lorem ipsum dolor sit amet"
  ]
}
```

### Expected Response

**Status:** `200`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
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
  "temperature": 0.0,
  "max_tokens": 1,
  "stream": true,
  "top_p": 0.0,
  "stop": [
    "Lorem ipsum dolor sit amet",
    "Test with 'single' quotes",
    "Test with \"double\" quotes"
  ]
}
```

### Expected Response

**Status:** `200`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
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
  "temperature": 0.0,
  "max_tokens": 1,
  "stream": true,
  "top_p": 0.5,
  "stop": []
}
```

### Expected Response

**Status:** `200`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
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
  "temperature": 0.0,
  "max_tokens": 1,
  "stream": true,
  "top_p": 0.5,
  "stop": [
    "Lorem ipsum dolor sit amet"
  ]
}
```

### Expected Response

**Status:** `200`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
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
  "temperature": 0.0,
  "max_tokens": 1,
  "stream": true,
  "top_p": 0.5,
  "stop": [
    "Lorem ipsum dolor sit amet",
    "Test with 'single' quotes",
    "Test with \"double\" quotes"
  ]
}
```

### Expected Response

**Status:** `200`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
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
  "temperature": 0.0,
  "max_tokens": 1,
  "stream": true,
  "top_p": 1.0,
  "stop": []
}
```

### Expected Response

**Status:** `200`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
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
  "temperature": 0.0,
  "max_tokens": 1,
  "stream": true,
  "top_p": 1.0,
  "stop": [
    "Lorem ipsum dolor sit amet"
  ]
}
```

### Expected Response

**Status:** `200`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
}
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
  "temperature": 0.0,
  "max_tokens": 1,
  "stream": true,
  "top_p": 1.0,
  "stop": [
    "Lorem ipsum dolor sit amet",
    "Test with 'single' quotes",
    "Test with \"double\" quotes"
  ]
}
```

### Expected Response

**Status:** `200`

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

**Status:** `501`

```json
{
  "detail": "Streaming not yet implemented"
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
  "temperature": 0.0,
  "max_tokens": 1,
  "stream": false,
  "top_p": 0.0,
  "stop": []
}
```

### Expected Response

**Status:** `200`

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
  "id": "chatcmpl-c5d0d8004b8f4356abfd6cd2",
  "object": "chat.completion",
  "created": 1769830821,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": ""
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 1,
    "total_tokens": 20
  }
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

**Status:** `200`

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
  "created_at": "2026-01-31T03:40:24.049794Z",
  "response": "The capital of France is **Paris**. \n\nDo you want to know more about Paris?",
  "done": true,
  "context": [],
  "total_duration": 0,
  "load_duration": 0,
  "prompt_eval_count": 21,
  "prompt_eval_duration": 0,
  "eval_count": 20,
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
  "top_k": 1
}
```

### Expected Response

**Status:** `200`

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
  "top_k": 500000
}
```

### Expected Response

**Status:** `200`

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
  "top_k": 1000000
}
```

### Expected Response

**Status:** `200`

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
  "top_p": 0.5,
  "top_k": 1
}
```

### Expected Response

**Status:** `200`

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
  "top_p": 0.5,
  "top_k": 500000
}
```

### Expected Response

**Status:** `200`

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
  "top_p": 0.5,
  "top_k": 1000000
}
```

### Expected Response

**Status:** `200`

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
  "top_p": 1.0,
  "top_k": 1
}
```

### Expected Response

**Status:** `200`

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
  "top_p": 1.0,
  "top_k": 500000
}
```

### Expected Response

**Status:** `200`

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
  "top_p": 1.0,
  "top_k": 1000000
}
```

### Expected Response

**Status:** `200`

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
  "temperature": 0.123456789,
  "top_p": 0.0,
  "top_k": 1
}
```

### Expected Response

**Status:** `200`

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
