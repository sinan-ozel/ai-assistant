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
  "stream": false
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503`

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
  "message": "Okay! To give you the weather, I need to know your location. Could you please tell me where you are? \ud83d\ude0a \n",
  "role": "assistant",
  "created": 1770008701,
  "usage": {
    "prompt_tokens": 44,
    "completion_tokens": 28,
    "total_tokens": 72
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
  "stream": true
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503`

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
  "stream": false
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503`

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
  "message": "Okay! I understand. It\u2019s just some placeholder text. Is there anything I can help you with regarding this text or anything else?",
  "role": "assistant",
  "created": 1770008703,
  "usage": {
    "prompt_tokens": 43,
    "completion_tokens": 29,
    "total_tokens": 72
  }
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
  "user_id": "Test with 'single' quotes",
  "stream": true
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503`

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
  "user_id": "Test with 'single' quotes",
  "stream": false
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503`

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
  "message": "Okay, I understand. You\u2019ve provided \u201cLorem ipsum dolor sit amet\u201d. Is there anything I can help you with regarding this text? For example, would you like me to:\n\n*   Explain it?\n*   Translate it?\n*   Suggest a potential use case for it?",
  "role": "assistant",
  "created": 1770008707,
  "usage": {
    "prompt_tokens": 43,
    "completion_tokens": 61,
    "total_tokens": 104
  }
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
  "user_id": "Test with \"double\" quotes",
  "stream": true
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503`

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
  "user_id": "Test with \"double\" quotes",
  "stream": false
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503`

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
  "message": "Okay! You've started with the classic placeholder text. What would you like to do with it?  Do you want me to:\n\n*   **Analyze it?** (e.g., identify the word length, letter frequency, etc.)\n*   **Generate something related to it?** (e.g., a sentence, a poem, a story excerpt)\n*   **Just acknowledge it?** (e.g., \u201cOkay, that\u2019s Lorem Ipsum.\u201d)\n\nLet me know how I can help!",
  "role": "assistant",
  "created": 1770008713,
  "usage": {
    "prompt_tokens": 43,
    "completion_tokens": 110,
    "total_tokens": 153
  }
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
  "user_id": "Test:with:colons",
  "stream": true
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503`

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
  "user_id": "Test:with:colons",
  "stream": false
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503`

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
  "message": "Okay, I understand. You've provided the classic \"Lorem Ipsum\" placeholder text. \n\nIs there anything I can help you with regarding it, or is there something else you'd like to discuss? For example, would you like me to:\n\n*   Explain its purpose?\n*   Generate some variations?\n*   Answer a question about it?",
  "role": "assistant",
  "created": 1770008717,
  "usage": {
    "prompt_tokens": 43,
    "completion_tokens": 76,
    "total_tokens": 119
  }
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
  "user_id": "Test\\with\\backslashes",
  "stream": true
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503`

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
  "user_id": "Test\\with\\backslashes",
  "stream": false
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 501 or 503`

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
  "message": "Okay, I understand. You\u2019ve provided the text \"Lorem ipsum dolor sit amet\". \n\nIs there anything I can help you with regarding this text? For example, would you like me to:\n\n*   Analyze it?\n*   Generate text based on it?\n*   Answer a question about it?",
  "role": "assistant",
  "created": 1770008721,
  "usage": {
    "prompt_tokens": 43,
    "completion_tokens": 66,
    "total_tokens": 109
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
  "messages": [
    {
      "role": "user",
      "content": "What is the capital of France?"
    }
  ]
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "id": "chatcmpl-2da41d2275d94366be0c7a8f",
  "object": "chat.completion",
  "created": 1770008723,
  "model": "ollama/gemma3:1b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is Paris. \ud83d\ude0a"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 21,
    "completion_tokens": 9,
    "total_tokens": 30
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
  ]
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "id": "chatcmpl-cb1b58076dec41a59bd38589",
  "object": "chat.completion",
  "created": 1770008729,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic \"Lorem Ipsum\" placeholder text. \n\nIs there anything I can help you with regarding it? For example, would you like me to:\n\n*   **Explain its purpose?** (It's a placeholder text used in book design and printing to simulate the appearance of text without needing actual content.)\n*   **Give you some examples of how it's used?** \n*   **Generate some text *using* Lorem Ipsum?** (I can create a short paragraph, or even a longer piece of text.)"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 121,
    "total_tokens": 140
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
  ]
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "id": "chatcmpl-d69d865c7eb74b5b8392e284",
  "object": "chat.completion",
  "created": 1770008736,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic placeholder text, \"Lorem ipsum dolor sit amet.\" \n\nIs there anything I can do with this text? For example, would you like me to:\n\n*   **Translate it?** (It's Latin, so it's not a direct translation)\n*   **Analyze it?** (For example, determine its purpose - it's often used for placeholder text in print design)\n*   **Generate a continuation?** (If you give me a starting point, I could try to continue the text in a similar style)\n*   **Something else?**\n\nLet me know what you'd like me to do."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 145,
    "total_tokens": 164
  }
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
    },
    {
      "role": "system",
      "content": "Test with 'single' quotes"
    },
    {
      "role": "system",
      "content": "Test with \"double\" quotes"
    }
  ]
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "id": "chatcmpl-c8d022cff8834881a95ed6f7",
  "object": "chat.completion",
  "created": 1770008743,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided a sample of Lorem ipsum text, formatted with single and double quotes. \n\nThis is a common practice in the printing and design industry for placeholder text. It's used during the initial stages of preparing a document to showcase the design and layout without the actual content.\n\nIs there anything specific you'd like me to do with this text? For example, would you like me to:\n\n*   Analyze it? (e.g., identify the stylistic choices?)\n*   Generate similar text?\n*   Convert it to a different format?\n*   Explain its purpose?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 31,
    "completion_tokens": 129,
    "total_tokens": 160
  }
}
```

---

## Test #19 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/chat/completions`

### Request Body

```json
{
  "model": "Test with 'single' quotes",
  "messages": [
    {
      "role": "system",
      "content": "Lorem ipsum dolor sit amet"
    }
  ]
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "id": "chatcmpl-3a2354be347e4194b91ebb8f",
  "object": "chat.completion",
  "created": 1770008749,
  "model": "Test with 'single' quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic \"Lorem ipsum\" placeholder text. \n\nIt's a placeholder text often used in design and printing to show the visual layout of a document without relying on actual content. \n\nIs there anything you'd like me to do with it? For example, would you like me to:\n\n*   **Generate more Lorem Ipsum text?** (e.g., a longer passage)\n*   **Analyze it?** (e.g., identify key words?)\n*   **Explain its purpose?**\n*   **Something else?**"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 125,
    "total_tokens": 144
  }
}
```

---

## Test #20 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/chat/completions`

### Request Body

```json
{
  "model": "Test with 'single' quotes",
  "messages": [
    {
      "role": "system",
      "content": "Lorem ipsum dolor sit amet"
    }
  ]
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "id": "chatcmpl-ca290da644574bf1a0e86438",
  "object": "chat.completion",
  "created": 1770008756,
  "model": "Test with 'single' quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic placeholder text: \"Lorem ipsum dolor sit amet\". \n\nIt's a common placeholder text used in the printing and design industries to provide visual filler in documents without needing actual content. \n\nIs there anything you'd like me to do with it? For example, would you like me to:\n\n*   **Translate it?** (It's Latin, but it's often used as a placeholder.)\n*   **Explain its purpose?** (It's a stylistic placeholder designed to show the layout and structure of a document, without meaning anything.)\n*   **Generate variations or alternatives?** (Perhaps suggest a slightly different phrasing?)\n*   **Something else entirely?**"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 155,
    "total_tokens": 174
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
  "model": "Test with 'single' quotes",
  "messages": [
    {
      "role": "system",
      "content": "Lorem ipsum dolor sit amet"
    },
    {
      "role": "system",
      "content": "Test with 'single' quotes"
    },
    {
      "role": "system",
      "content": "Test with \"double\" quotes"
    }
  ]
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "id": "chatcmpl-c61f4cb590d44ebe861d15d7",
  "object": "chat.completion",
  "created": 1770008766,
  "model": "Test with 'single' quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided a seemingly random string of text: \"Lorem ipsum dolor sit ametTest with 'single' quotesTest with \\\"double\\\" quotes.\" \n\nIt's a classic example used in the printing industry to display text in a placeholder format while the final text content is created.  It's designed to mimic the appearance of real text but with no meaningful content. \n\nIs there anything specific you'd like me to do with this?  For example, would you like me to:\n\n*   **Analyze the text?** (e.g., identify patterns, analyze its structure)\n*   **Generate text based on this example?** (e.g., create a paragraph using this style)\n*   **Answer a question about it?** (e.g., \"What does this usually signify?\")\n*   **Just acknowledge the text?**"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 31,
    "completion_tokens": 186,
    "total_tokens": 217
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
  "model": "Test with \"double\" quotes",
  "messages": [
    {
      "role": "system",
      "content": "Lorem ipsum dolor sit amet"
    }
  ]
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "id": "chatcmpl-16e862df0aae4fe4ad863354",
  "object": "chat.completion",
  "created": 1770008772,
  "model": "Test with \"double\" quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic \"Lorem Ipsum\" text. \n\nIs there anything you'd like me to do with it? For example, would you like me to:\n\n*   **Analyze it?** (e.g., identify its purpose, or explain its linguistic properties)\n*   **Generate text based on it?** (e.g., a paragraph or short story)\n*   **Answer a question about it?** (e.g., \"What does it represent?\")\n*   **Something else entirely?**"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 118,
    "total_tokens": 137
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
  "model": "Test with \"double\" quotes",
  "messages": [
    {
      "role": "system",
      "content": "Lorem ipsum dolor sit amet"
    }
  ]
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "id": "chatcmpl-1d5b91948efe4997bcaa530b",
  "object": "chat.completion",
  "created": 1770008780,
  "model": "Test with \"double\" quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic \"Lorem ipsum\" placeholder text. \n\nIt's a placeholder text used in the printing and design industries to display text in a way that mimics the appearance of the final printed document without showing the actual content. \n\nIs there anything you'd like me to do with it? For example, would you like me to:\n\n*   **Generate more Lorem Ipsum text?** (e.g., a longer passage, a specific style)\n*   **Explain the purpose of Lorem Ipsum?**\n*   **Translate it to another language?** (though it's not really a translation)\n*   **Do something else with it?**"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 147,
    "total_tokens": 166
  }
}
```

---

## Test #24 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/chat/completions`

### Request Body

```json
{
  "model": "Test with \"double\" quotes",
  "messages": [
    {
      "role": "system",
      "content": "Lorem ipsum dolor sit amet"
    },
    {
      "role": "system",
      "content": "Test with 'single' quotes"
    },
    {
      "role": "system",
      "content": "Test with \"double\" quotes"
    }
  ]
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "id": "chatcmpl-5ce1019680294cf0be25402d",
  "object": "chat.completion",
  "created": 1770008791,
  "model": "Test with \"double\" quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided a classic example of Lorem Ipsum text, which is frequently used in typesetting and design. It's placeholder text that doesn't have a meaningful visual appearance.\n\n**Here's a slightly more expanded version of the text you provided:**\n\nLorem ipsum dolor sit ametTest with 'single' quotesTest with \"double\" quotes \n\n**Why this is used:**\n\n* **Placeholder Text:** It's used to fill out document templates before the actual content is finalized.\n* **Readability:** It provides a consistent and easily-readable block of text that allows designers and developers to focus on layout and visual appearance without worrying about a visible sentence.\n* **Testing:**  It's employed to test fonts, layouts, and visual effects before using actual content.\n\nDo you have any specific questions about Lorem Ipsum or want me to do anything with this text?  For example, would you like me to:\n\n*   Analyze it?\n*   Generate some variations?\n*   Explain its purpose in more detail?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 31,
    "completion_tokens": 219,
    "total_tokens": 250
  }
}
```

---

## Test #25 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/chat/completions`

### Request Body

```json
{
  "model": "Test:with:colons",
  "messages": [
    {
      "role": "system",
      "content": "Lorem ipsum dolor sit amet"
    }
  ]
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "id": "chatcmpl-b2db142c351f45538f23c756",
  "object": "chat.completion",
  "created": 1770008796,
  "model": "Test:with:colons",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic \"Lorem ipsum\" text. \n\nIs there anything I can do with it? For example, would you like me to:\n\n*   **Generate some text based on it?** (e.g., a story, a poem, a paragraph)\n*   **Explain what it is?**\n*   **Provide some related information?**\n*   **Simply acknowledge it?**"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 93,
    "total_tokens": 112
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

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "created_at": "2026-02-02T05:06:38.097961Z",
  "response": "The capital of France is **Paris**. \n\nIt\u2019s a great city! \ud83d\ude0a \n\nWould you like to know more about Paris?",
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
  "top_k": 1
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "top_k": 500000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "top_k": 1000000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "top_p": 0.5,
  "top_k": 1
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "top_p": 0.5,
  "top_k": 500000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "top_p": 0.5,
  "top_k": 1000000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "top_p": 1.0,
  "top_k": 1
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "top_p": 1.0,
  "top_k": 500000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "top_p": 1.0,
  "top_k": 1000000
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "temperature": 0.123456789,
  "top_p": 0.0,
  "top_k": 1
}
```

### Expected Response

**Status:** `200 or 422 or 400 or 404 or 501`

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
  "max_tokens": 4096
}
```

### Expected Response

**Status:** `200 or 422`

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
  "result": "Please provide the user message you would like me to summarize.",
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 13,
    "total_tokens": 63
  }
}
```

---

## Test #38 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/summarize-text`

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

**Status:** `200 or 422`

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
    "prompt_tokens": 42,
    "completion_tokens": 1,
    "total_tokens": 43
  }
}
```

---

## Test #39 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/summarize-text`

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

**Status:** `200 or 422`

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
  "result": "Please provide the user message you would like me to clean up and summarize.",
  "usage": {
    "prompt_tokens": 42,
    "completion_tokens": 16,
    "total_tokens": 58
  }
}
```

---

## Test #40 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/summarize-text`

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

**Status:** `200 or 422`

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
  "result": "Please provide the user message you would like me to clean up and summarize.",
  "usage": {
    "prompt_tokens": 42,
    "completion_tokens": 16,
    "total_tokens": 58
  }
}
```

---

## Test #41 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/summarize-text`

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

**Status:** `200 or 422`

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
    "prompt_tokens": 42,
    "completion_tokens": 1,
    "total_tokens": 43
  }
}
```

---

## Test #42 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/summarize-text`

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

**Status:** `200 or 422`

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
  "result": "Please provide the user message you would like me to clean up and summarize.",
  "usage": {
    "prompt_tokens": 42,
    "completion_tokens": 16,
    "total_tokens": 58
  }
}
```

---

## Test #43 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/summarize-text`

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

**Status:** `200 or 422`

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
  "result": "Please provide the user message you would like me to clean up and summarize.",
  "usage": {
    "prompt_tokens": 42,
    "completion_tokens": 16,
    "total_tokens": 58
  }
}
```

---

## Test #44 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/summarize-text`

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

**Status:** `200 or 422`

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
    "prompt_tokens": 42,
    "completion_tokens": 1,
    "total_tokens": 43
  }
}
```

---

## Test #45 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/summarize-text`

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

**Status:** `200 or 422`

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
  "result": "Please provide the user message you would like me to summarize.",
  "usage": {
    "prompt_tokens": 42,
    "completion_tokens": 13,
    "total_tokens": 55
  }
}
```

---

## Test #46 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/summarize-text`

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

**Status:** `200 or 422`

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
  "result": "Please provide the user message you want me to summarize.",
  "usage": {
    "prompt_tokens": 42,
    "completion_tokens": 12,
    "total_tokens": 54
  }
}
```

---

## Test #47 ✅

📋 *Test case from OpenAPI example*

**Endpoint:** `POST /v1/summarize-text`

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

**Status:** `200 or 422`

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
    "prompt_tokens": 42,
    "completion_tokens": 1,
    "total_tokens": 43
  }
}
```

---
