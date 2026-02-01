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
  "message": "Okay! Right now, it\u2019s raining lightly in London, England. The temperature is around 15 degrees Celsius (59 degrees Fahrenheit).",
  "role": "assistant",
  "created": 1769931174,
  "usage": {
    "prompt_tokens": 84,
    "completion_tokens": 31,
    "total_tokens": 115
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
  "message": "Okay! It\u2019s a classic placeholder text. It\u2019s a placeholder used in design and typesetting to provide text to allow designers to see a page\u2019s layout without the need for actual content. \n\nIs there anything you\u2019d like to do with it?  Perhaps you want to know what it *generally* means, or maybe you want me to generate some text *around* it?",
  "role": "assistant",
  "created": 1769931179,
  "usage": {
    "prompt_tokens": 128,
    "completion_tokens": 82,
    "total_tokens": 210
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
  "message": "Okay! Let\u2019s just acknowledge that. \u201cLorem ipsum dolor sit amet\u201d is a placeholder text \u2013 a seemingly random string of text used in printing and design to fill space while the final design is being created. \n\nDo you want me to tell you a little bit about its origin?",
  "role": "assistant",
  "created": 1769931183,
  "usage": {
    "prompt_tokens": 115,
    "completion_tokens": 60,
    "total_tokens": 175
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
  "message": "Okay! It\u2019s a placeholder text, often used in design and marketing to display text in a way that mimics the appearance of real content without requiring actual content. It\u2019s a standard practice to avoid distracting from the design.\n\nDo you want me to explain what it *generally* represents, or would you like me to generate a similar phrase?",
  "role": "assistant",
  "created": 1769931189,
  "usage": {
    "prompt_tokens": 124,
    "completion_tokens": 72,
    "total_tokens": 196
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
  "message": "Okay, let's explore it further! It\u2019s a frequently used placeholder, and it\u2019s more than just a placeholder. It\u2019s a test text that\u2019s used in design and printing to fill space on a page before the final design is finalized. \n\nDo you want to know about:\n\n*   **The history of Lorem Ipsum?** (How it was originally created?)\n*   **Why it's used?** (Its purpose and benefits)\n*   **Different variations of Lorem Ipsum?** (e.g., with different fonts and styles)\n*   **How it\u2019s used in design?** (A little bit about its role in design workflows?)\n*   **Something else entirely?**",
  "role": "assistant",
  "created": 1769931198,
  "usage": {
    "prompt_tokens": 93,
    "completion_tokens": 154,
    "total_tokens": 247
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
  "message": "Okay! It\u2019s perfectly fine to just acknowledge it. It\u2019s a classic placeholder text. \n\nDo you want me to do anything with it?",
  "role": "assistant",
  "created": 1769931201,
  "usage": {
    "prompt_tokens": 124,
    "completion_tokens": 33,
    "total_tokens": 157
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
  "id": "chatcmpl-01097419cd80489eb8dd9119",
  "object": "chat.completion",
  "created": 1769931203,
  "model": "ollama/gemma3:1b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is **Paris**. \n\nWould you like to know more about Paris?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 21,
    "completion_tokens": 20,
    "total_tokens": 41
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

**Status:** `200`

```json
{
  "id": "chatcmpl-09fa0a506e6b41e3af55b81f",
  "object": "chat.completion",
  "created": 1769931211,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic placeholder text: \u201cLorem ipsum dolor sit amet.\u201d \n\nIt's a common placeholder text used in printing and design to provide a visual placeholder while typesetting and preparing a document. \n\nIs there anything specific you'd like me to do with this text? For example, would you like me to:\n\n*   **Translate it?** (It's Latin, but it's often used as a placeholder.)\n*   **Generate similar text?** (If you wanted to create a similar-looking placeholder for another purpose.)\n*   **Explain its purpose?** (It's a standard practice and has a specific historical context.)\n*   **Just acknowledge it?**"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 154,
    "total_tokens": 173
  }
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

**Status:** `200`

```json
{
  "id": "chatcmpl-7a473086e2e14ee5822cd3bd",
  "object": "chat.completion",
  "created": 1769931219,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic placeholder text: \"Lorem ipsum dolor sit amet.\" \n\nIt's a common placeholder text used in graphic design and typesetting to show a page layout without needing actual content. \n\nIs there anything you'd like me to do with this text?  For example, would you like me to:\n\n*   **Translate it?** (It's Latin, but often used as a placeholder)\n*   **Explain it?** (It's a placeholder, not actual text)\n*   **Generate a similar text?** (Perhaps a paragraph that fits the context)\n*   **Do something else with it?**"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 143,
    "total_tokens": 162
  }
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
  "id": "chatcmpl-5f8ab08d09354481af50533c",
  "object": "chat.completion",
  "created": 1769931229,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided a string containing \"Lorem ipsum dolor sit ametTest with 'single' quotesTest with \\\"double\\\" quotes\". \n\nIt's a classic placeholder text used in print and design to display text without requiring actual content. It's often used to demonstrate the visual layout of a document before the real content is finalized.\n\nDo you have any specific questions or tasks you'd like me to perform with this text? For example, are you looking for:\n\n*   **Analysis?** (e.g., count the number of words, identify specific phrases)\n*   **Translation?** (e.g., convert to another language)\n*   **Modification?** (e.g., make it longer/shorter, change formatting)\n*   **Something else?**\n\nLet me know what you'd like me to do!"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 31,
    "completion_tokens": 184,
    "total_tokens": 215
  }
}
```

---

## Test #19 ✅

🔧 *Test case generated from schema*

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
  "id": "chatcmpl-c1407b14b1e64f4caf79f372",
  "object": "chat.completion",
  "created": 1769931236,
  "model": "Test with 'single' quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic \"Lorem ipsum\" placeholder text. \n\nIs there anything specific you'd like me to do with it? For example, are you:\n\n*   **Wanting me to continue the text?** (I can continue writing in the same style, or write a different kind of text).\n*   **Looking for a translation?** (I can translate it into other languages if you specify).\n*   **Wanting to know about its purpose?** (It's a placeholder used in typesetting to display text without having to fill it with real content.)\n*   **Something else entirely?**\n\nLet me know how I can assist you!"
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

## Test #20 ✅

🔧 *Test case generated from schema*

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
  "id": "chatcmpl-f779870a618f4d10b62fcaa9",
  "object": "chat.completion",
  "created": 1769931243,
  "model": "Test with 'single' quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic \"Lorem ipsum\" placeholder text. \n\nIs there anything I can do with it? For example, would you like me to:\n\n*   **Analyze it?** (e.g., its structure, its use in a specific context)\n*   **Generate text around it?** (e.g., a paragraph of similar text)\n*   **Convert it to a different format?** (e.g., HTML, Markdown)\n*   **Just acknowledge it?** (Like \"That's a standard placeholder.\")\n\nLet me know what you have in mind."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 133,
    "total_tokens": 152
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
  "id": "chatcmpl-553180dc9a8641938d718fb8",
  "object": "chat.completion",
  "created": 1769931252,
  "model": "Test with 'single' quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided a string of text:\n\n\"Lorem ipsum dolor sit ametTest with 'single' quotesTest with \"double\" quotes\"\n\nThis is a common practice in the printing and design industry, particularly for placeholder text. It's a non-meaningful text meant to provide a visual structure and space for the final text to flow within.\n\nIs there anything specific you'd like me to do with this text? For example, would you like me to:\n\n*   **Analyze it?** (e.g., identify keywords, check for specific patterns?)\n*   **Generate text based on it?** (e.g., a short story or paragraph?)\n*   **Convert it to another format?** (e.g., a markdown list?)\n*   **Explain its purpose?**"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 31,
    "completion_tokens": 175,
    "total_tokens": 206
  }
}
```

---

## Test #22 ✅

🔧 *Test case generated from schema*

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
  "id": "chatcmpl-b2c916f2e93e4ccdaa58604d",
  "object": "chat.completion",
  "created": 1769931259,
  "model": "Test with \"double\" quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the standard placeholder text \"Lorem ipsum dolor sit amet\". \n\nIs there anything I can help you with regarding this text? For example, would you like me to:\n\n*   **Analyze it?** (e.g., identify its common use in typesetting)\n*   **Generate something related to it?** (e.g., a sentence using it?)\n*   **Explain its purpose?** (it's often used to demonstrate page layout without meaning)\n*   **Something else?** \n\nLet me know what you're interested in!"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 127,
    "total_tokens": 146
  }
}
```

---

## Test #23 ✅

🔧 *Test case generated from schema*

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
  "id": "chatcmpl-a6eaffefb4f24072b5af3300",
  "object": "chat.completion",
  "created": 1769931267,
  "model": "Test with \"double\" quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic placeholder text \"Lorem ipsum dolor sit amet\". \n\nIs there anything you'd like me to do with it?  For example, would you like me to:\n\n*   **Analyze it?** (e.g., identify its structure, or suggest possible interpretations?)\n*   **Generate text based on it?** (e.g., write a story, a poem, or a response to a prompt?)\n*   **Explain its purpose?** (It's a placeholder text \u2013 it doesn't *mean* anything, but it's used for design because it's meaningless.)\n*   **Something else?**"
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

## Test #24 ✅

🔧 *Test case generated from schema*

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
  "id": "chatcmpl-c66cdd913398441784330265",
  "object": "chat.completion",
  "created": 1769931276,
  "model": "Test with \"double\" quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided a string of text:\n\n`Lorem ipsum dolor sit ametTest with 'single' quotesTest with \"double\" quotes`\n\nThis is a common practice in graphic design and printing when creating placeholder text. It's a large, seemingly random text block used to fill space in a document before the actual content is finalized.  \n\n**Essentially, it's a placeholder that allows designers to see how the text will look in a real document.**\n\nDo you want me to do anything with this text? For example, would you like me to:\n\n*   Analyze it? (e.g., identify words, phrases, common patterns)\n*   Generate text that *looks* like this? (e.g., create a paragraph with similar style)\n*   Do something else with it?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 31,
    "completion_tokens": 173,
    "total_tokens": 204
  }
}
```

---

## Test #25 ✅

🔧 *Test case generated from schema*

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
  "id": "chatcmpl-dd9b810ae2cc4eb19699d211",
  "object": "chat.completion",
  "created": 1769931283,
  "model": "Test:with:colons",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic placeholder text: \"Lorem ipsum dolor sit amet\". \n\nIs there anything I can help you with regarding this text? For example, are you:\n\n*   **Looking for a translation?** (It's a placeholder \u2013 it doesn't have a meaning in any language.)\n*   **Trying to understand its purpose?** (It's a common practice in typesetting and design to provide a visually similar text to a full document without needing actual content.)\n*   **Wanting to generate something similar?** (If you're creating a test or a placeholder text for a document.)"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 135,
    "total_tokens": 154
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
  "created_at": "2026-02-01T07:34:45.233586Z",
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

**Status:** `200`

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
  "result": "Please provide the user message you want me to summarize. I need the text of the message to fulfill your request.",
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 24,
    "total_tokens": 74
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
  "max_tokens": 1
}
```

### Expected Response

**Status:** `200`

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

🔧 *Test case generated from schema*

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

**Status:** `200`

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

🔧 *Test case generated from schema*

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

**Status:** `200`

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

🔧 *Test case generated from schema*

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

**Status:** `200`

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

🔧 *Test case generated from schema*

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

**Status:** `200`

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

🔧 *Test case generated from schema*

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

**Status:** `200`

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

🔧 *Test case generated from schema*

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

**Status:** `200`

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

🔧 *Test case generated from schema*

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

**Status:** `200`

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

## Test #46 ✅

🔧 *Test case generated from schema*

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

**Status:** `200`

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

## Test #47 ✅

🔧 *Test case generated from schema*

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

**Status:** `200`

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
