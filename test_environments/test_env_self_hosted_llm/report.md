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
  "message": "Okay, let\u2019s check the weather for **London, England**. \n\nHere\u2019s the forecast:\n\nCurrently, London is experiencing light rain with a temperature of 15\u00b0C (59\u00b0F). It's expected to continue with a high of 18\u00b0C (64\u00b0F) later today.",
  "role": "assistant",
  "created": 1770009989,
  "usage": {
    "prompt_tokens": 1532,
    "completion_tokens": 70,
    "total_tokens": 1602
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
  "message": "### Assistant:\nExcellent! Elaborating on the \u201cfiller text\u201d concept \u2013 it\u2019s a brilliant strategy. It\u2019s essentially a way to build a visual skeleton for the page, allowing designers to quickly evaluate the impact of different elements without needing to create fully designed pages. The lack of meaning, coupled with the ability to change text and formatting, makes it incredibly useful for quickly understanding and testing visual layouts. It\u2019s a cornerstone of many design processes, even when full design documents are finalized. Would you like me to share some statistics or examples of how it's used in different design contexts, or perhaps discuss its relationship to other placeholder text techniques?",
  "role": "assistant",
  "created": 1770010007,
  "usage": {
    "prompt_tokens": 1265,
    "completion_tokens": 134,
    "total_tokens": 1399
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
  "message": "### Assistant:\n\nOkay, fantastic! Let\u2019s really dive into how this grid system influenced the typography. It\u2019s a really compelling point. The grid, as you\u2019ve noted, wasn\u2019t just about arranging words; it was about establishing a *visual rhythm* and a deliberate \u2018lens\u2019 for the reader. They used the three points \u2013 top, bottom, and middle \u2013 to guide the eye through the text, creating a sense of balance and emphasis.\n\nConsider this: they often placed key phrases or ideas at the intersection of the columns. This wasn\u2019t random placement; it was strategically positioned to draw attention to crucial information.  The grid, in essence, acted as a framework for the text\u2019s visual hierarchy.\n\nIt\u2019s a stark example of early design thinking \u2013 a minimalist system that dictated the *direction* of the reader\u2019s gaze. They were creating a visual map for the text, influencing how the reader perceived the content. It\u2019s clear they were prioritizing certain elements \u2013 highlighting key phrases, creating a sense of visual balance, and guiding the reader\u2019s eye through the text.\n\nWould you like me to analyze a specific example of how they used the grid to create particular visual groupings \u2013 perhaps a focus on a certain phrase or concept? Or would you prefer to discuss the overall effect of this early testing method on the book\u2019s typography choices?",
  "role": "assistant",
  "created": 1770010039,
  "usage": {
    "prompt_tokens": 1954,
    "completion_tokens": 283,
    "total_tokens": 2237
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
  "message": "Okay, let\u2019s just acknowledge the placeholder text. It\u2019s a very common placeholder! \ud83d\ude0a  It\u2019s a placeholder, and I\u2019m here to help if you need anything else with it.",
  "role": "assistant",
  "created": 1770010052,
  "usage": {
    "prompt_tokens": 1187,
    "completion_tokens": 43,
    "total_tokens": 1230
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
  "message": "Okay, I understand. You\u2019re just providing the text. How can I help you with it, or perhaps with something else related to writing or placeholder text?",
  "role": "assistant",
  "created": 1770010063,
  "usage": {
    "prompt_tokens": 1037,
    "completion_tokens": 34,
    "total_tokens": 1071
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
  "message": "That\u2019s right! It\u2019s a placeholder text. \ud83d\ude0a",
  "role": "assistant",
  "created": 1770010072,
  "usage": {
    "prompt_tokens": 849,
    "completion_tokens": 14,
    "total_tokens": 863
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
  "id": "chatcmpl-2176311d67614e38bdb5160d",
  "object": "chat.completion",
  "created": 1770010074,
  "model": "ollama/gemma3:1b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is **Paris**. \n\n\ud83d\ude0a"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 21,
    "completion_tokens": 12,
    "total_tokens": 33
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
  "id": "chatcmpl-cf152bd59e2747d0b1f5fa06",
  "object": "chat.completion",
  "created": 1770010079,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic placeholder text \"Lorem ipsum dolor sit amet.\" \n\nIt's a common practice when creating documents like books or articles to display text without requiring a meaningful content. It's purely for visual purposes and doesn't have any actual meaning. \n\nDo you have any questions about it, or would you like me to do anything with it (like:\n\n*   Explain it?\n*   Provide some context about its use?\n*   Generate similar text?)"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 107,
    "total_tokens": 126
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
  "id": "chatcmpl-c831348ba2094408bbb7ce2f",
  "object": "chat.completion",
  "created": 1770010085,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the standard \"Lorem ipsum\" text. \n\nIs there anything I can do with it? For example, would you like me to:\n\n*   **Analyze it?** (e.g., count words, identify patterns)\n*   **Generate text based on it?** (e.g., a short story, a paragraph)\n*   **Provide a different context?** (e.g., a description of its purpose) \n\nLet me know what you'd like me to do!"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 115,
    "total_tokens": 134
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
  "id": "chatcmpl-f8918470d3984bcf99f5d529",
  "object": "chat.completion",
  "created": 1770010092,
  "model": "Lorem ipsum dolor sit amet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided a text snippet consisting of two instances of \"single\" and \"double\" quotes. \n\nIs there anything specific you'd like me to do with this text? For example, would you like me to:\n\n*   **Analyze it?** (e.g., identify the words, count characters, etc.)\n*   **Generate text *using* these quotes?** (e.g., create a sentence using \"single\" and \"double\" quotes)\n*   **Something else?**\n\nLet me know how I can help."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 31,
    "completion_tokens": 123,
    "total_tokens": 154
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
  "id": "chatcmpl-c2baed541e35465d81c9a519",
  "object": "chat.completion",
  "created": 1770010099,
  "model": "Test with 'single' quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic placeholder text: \"Lorem ipsum dolor sit amet\". \n\nIs there anything specific you'd like me to do with it? For example, would you like me to:\n\n*   **Explain it?** (It's a placeholder, typically used in typesetting to fill a page with text while the final content is developed.)\n*   **Generate text based on it?** (I could write a short paragraph, a sentence, or a story using the placeholder.)\n*   **Suggest a translation?** (It's Latin, and generally means \"pain is not felt\" \u2013 a common placeholder for typesetting.)\n*   **Something else entirely?**\n\nLet me know how I can help!"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 157,
    "total_tokens": 176
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
  "id": "chatcmpl-6ef4ec30723b4a38a11f5e41",
  "object": "chat.completion",
  "created": 1770010104,
  "model": "Test with 'single' quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "This is the classic placeholder text \u2013 the beginning of a page of Lorem Ipsum. It\u2019s a seemingly random selection of Latin text designed to simulate the appearance of page content in a document without requiring actual text. \n\nIt's a common practice in graphic design and typesetting to provide a placeholder until the final design is finalized. \n\nDo you have any questions about it, or would you like to know anything else related to it?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 89,
    "total_tokens": 108
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
  "id": "chatcmpl-f7d80ef68e034a9ba2ea2482",
  "object": "chat.completion",
  "created": 1770010106,
  "model": "Test with 'single' quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, here's the text presented as requested:\n\nLorem ipsum dolor sit ametTest with 'single' quotesTest with \"double\" quotes\n"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 31,
    "completion_tokens": 31,
    "total_tokens": 62
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
  "id": "chatcmpl-cd749570e33f453dacceb536",
  "object": "chat.completion",
  "created": 1770010113,
  "model": "Test with \"double\" quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the standard placeholder text: \"Lorem ipsum dolor sit amet.\" \n\nIs there anything specific you'd like me to do with this text? For example, would you like me to:\n\n*   **Translate it?** (I can provide a basic translation - though it's not very accurate for this purpose.)\n*   **Analyze it?** (Perhaps you want me to identify its purpose - it's a placeholder text used in print design.)\n*   **Generate variations?** (Perhaps you'd like a slightly different version?)\n*   **Something else?**\n\nLet me know how I can help!"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 140,
    "total_tokens": 159
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
  "id": "chatcmpl-ea3231d36a1e4470a37a8358",
  "object": "chat.completion",
  "created": 1770010119,
  "model": "Test with \"double\" quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic \"Lorem ipsum\" placeholder text. \n\nIs there anything I can do with it? For example, would you like me to:\n\n*   **Analyze it?** (e.g., count words, highlight specific patterns?)\n*   **Generate text based on it?** (e.g., a paragraph, a story, etc.)\n*   **Translate it?**\n*   **Something else?**\n\nJust let me know what you're interested in!"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 111,
    "total_tokens": 130
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
  "id": "chatcmpl-9a011bd5914049eb85ee3064",
  "object": "chat.completion",
  "created": 1770010127,
  "model": "Test with \"double\" quotes",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided a very short example of Lorem Ipsum and a test with \"single\" and \"double\" quotes. \n\nIs there anything specific you'd like me to do with this? For example, would you like me to:\n\n*   **Generate more Lorem Ipsum text?** (e.g., a paragraph, a set of sentences)\n*   **Explain the purpose of Lorem Ipsum?** (It's used as a placeholder in typesetting to provide a visual structure without requiring actual content)\n*   **Create a test that uses \"single\" and \"double\" quotes?** (Perhaps you'd like to see a little bit of a sentence that incorporates both)?\n*   **Something else entirely?**"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 31,
    "completion_tokens": 157,
    "total_tokens": 188
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
  "id": "chatcmpl-520c1851668e4c0e917212f8",
  "object": "chat.completion",
  "created": 1770010133,
  "model": "Test:with:colons",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Okay, I understand. You've provided the classic \"Lorem ipsum\" text. \n\nIs there anything you'd like me to do with it? For example, would you like me to:\n\n*   **Analyze it?** (e.g., identify the language, or describe its purpose?)\n*   **Generate variations?** (e.g., different lengths, different fonts?)\n*   **Explain its significance?** \n*   **Something else entirely?**"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 102,
    "total_tokens": 121
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
  "created_at": "2026-02-02T05:28:55.408758Z",
  "response": "The capital of France is **Paris**. \n\nDo you want to know more about Paris, like its history or famous landmarks?",
  "done": true,
  "context": [],
  "total_duration": 0,
  "load_duration": 0,
  "prompt_eval_count": 21,
  "prompt_eval_duration": 0,
  "eval_count": 27,
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
