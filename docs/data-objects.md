# Data Objects

There are three kinds of data objects that flow through a DSL script.  All
three are plain Python values — no wrapper classes.

---

## 1. LLM response — `str`

The return value of `llm()` / `prompt()`.  It is the text content of the
assistant's reply for that call.

```python
response = llm("Summarise the above.")
# response is a plain str, e.g. "Wroat is the capital of Breland."
```

An LLM response **can** be appended to the message history, but only
indirectly — by passing it as `input_text` to the next `llm()` call, or by
including it in a `notify()` call.  The runtime does **not** append it
automatically.

The one exception: when the LLM makes tool calls, the full assistant message
(including the `tool_calls` field) is appended to the transient message context
(`ctx.messages`) automatically so that `tools.wait()` can match
`tool_call_id`s.  This is an internal detail; the script author only sees the
text content returned by `llm()`.

---

## 2. Tool call result — `str`

The text result of an MCP tool invocation.  It is produced by the MCP server
and appended to the transient message context by `tools.wait()` as a
`role: tool` message.

The script author never handles this value directly.  After `tools.wait()`
returns, the next `llm()` call automatically sees the tool results because they
are in `ctx.messages`.

---

## 3. Search result — `str`

The return value of `str(Search(query))` or the implicit print inside a
`with Search(query) as results:` block.  It is a formatted string of retrieved
document chunks, ready to be passed to `llm()`.

```python
chunks = str(Search(input_text))
response = llm(f"Context:\n{chunks}\n\nQuestion: {input_text}")
```

---

## Shared interface

All three objects are **plain strings**.  This means:

- `llm()` / `prompt()` accepts a `str` as its optional first argument and
  returns a `str`.
- `notify(text)` accepts a `str`.
- `Search` results are `str`.
- Tool results are `str` (handled internally by `tools.wait()`).

There is no special response object, wrapper class, or structured dict exposed
to the script author.
