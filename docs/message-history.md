# Message History

There are two distinct message lists in the system.  Understanding the
difference is important for writing correct DSL scripts.

---

## 1. Persistent history — Redis `memory.messages`

Stored in Redis and loaded at the start of every request for the same
conversation.  Contains only the finished user/assistant exchange pairs from
previous turns.

**Mutated exactly twice per request:**

1. **Before the script runs** — the current user message is appended (as
   part of building `init_messages` for the DSL context).
2. **After the script finishes** — the final assistant response (from
   `notify()` or the last `llm()` call) is appended.

Nothing that happens inside the script touches `memory.messages`.

---

## 2. Transient context — `ctx.messages`

Lives only for the duration of one request.  Starts as a snapshot of:

```
[system message] + [fitted conversation history] + [current user message]
```

Grows during the script when tool calls happen:

| Event | What is appended |
|-------|-----------------|
| LLM makes tool calls (inside `llm()`) | `{"role": "assistant", "content": ..., "tool_calls": [...]}` |
| `tools.wait()` collects a result | `{"role": "tool", "tool_call_id": ..., "content": ...}` |

**Never** mutated by:

- Plain `llm()` text responses
- `input_text` passed to `llm(input_text=...)`
- `notify()`
- `Search` / `search`

After the script finishes, `ctx.messages` is discarded.  Only the final
response text flows into `memory.messages`.

---

## Request lifecycle diagram

```
Redis memory.messages (before request)
  [user: "prev turn"]
  [assistant: "prev reply"]
         │
         ▼
Build init_messages:
  [system]
  [user: "prev turn"]        ← fitted history
  [assistant: "prev reply"]
  [user: "current message"]  ← appended here
         │
         ▼
DSL script runs — ctx.messages grows only on tool calls
  [system]
  [user: "prev turn"]
  [assistant: "prev reply"]
  [user: "current message"]
  [assistant + tool_calls]   ← if llm() triggers tool calls
  [tool: result]             ← after tools.wait()
         │
         ▼
Script finishes → final_response = last llm() / notify() text
         │
         ▼
Redis memory.messages (after request)
  [user: "prev turn"]
  [assistant: "prev reply"]
  [user: "current message"]  ← appended now
  [assistant: final_response] ← appended now
```

---

## What `message_history` means inside a non-interactive script

In non-interactive `prompt.py` (no `llm()` / `notify()` / `McpServer`), the
injected `message_history` variable is a mutable copy of the conversation
history that the script can inspect or modify before the implicit LLM call.
Changes to it affect only the current request — not the Redis store.
