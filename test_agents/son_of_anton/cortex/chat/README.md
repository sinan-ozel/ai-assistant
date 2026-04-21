# Python DSL Examples for Prompt Customization

This directory contains the DSL configuration for the son_of_anton agent.

## Active Files

- **`prompt.py`** - The ACTIVE prompt DSL script (currently Level 0 - minimal)
- **`advanced_prompt.py`** - REFERENCE ONLY (not executed, demonstrates Level 12 patterns)

## How It Works

The agent chat endpoint looks for `prompt.py` (or `agent.py`) in the cortex directory
specified by the `CORTEX_FOLDER` environment variable.

**The DSL loader ONLY executes:**
- `prompt.py` (preferred)
- `agent.py` (fallback)

All other `.py` files are ignored and can serve as references or backups.

### DSL Contract

1. **Module docstring** → System prompt
2. **`print()` statements** → User message(s)
3. **`agent` object** → Model/parameter configuration
4. **`message_history`** → Mutable conversation list
5. **Blank lines in output** → Split into multiple user messages

### Available Variables

Scripts have access to:
- `input_text`: The user's input message
- `message_history`: List of conversation messages (mutable)
- `agent`: Configuration object with properties:
  - `agent.model` - Override model selection
  - `agent.temperature` - Sampling temperature
  - `agent.max_tokens` - Maximum tokens
  - `agent.stream` - Enable streaming
  - `agent.stream_format` - "sse" or "ndjson"
  - `agent.use_tools("tool1", "tool2")` - Enable tools
  - `agent.tool_choice` - Preferred tool
  - `agent.params["key"]` - Free-form parameters

## Examples

### Level 0 - Minimal (Just Pass Through)

```python
"""
You are a helpful assistant.
"""

print(input_text)
```

### Level 1 - Prompt Template

```python
"""
You rewrite text to be clearer and shorter.
"""

print(f"Rewrite clearly:\n\n{input_text}")
```

### Level 2 - Use Conversation History

```python
"""
Answer using prior context if relevant.
"""

if message_history:
    last = message_history[-1]["content"]
    print(f"Previous: {last}")
    print()  # Blank line = separate message

print(f"Question: {input_text}")
```

### Level 3 - Parameter Control

```python
"""
You are a precise technical assistant.
"""

agent.temperature = 0
agent.max_tokens = 200

print(input_text)
```

### Level 4 - Streaming Configuration

```python
"""
Explain for a beginner.
"""

agent.model = "fast-model"
agent.stream = True
agent.stream_format = "ndjson"

print(input_text)
```

### Level 7 - Memory Injection

```python
"""
You are strict and concise.
"""

# Inject additional system constraints
message_history.append({
    "role": "system",
    "content": "Never exceed 3 sentences."
})

print(input_text)
```

### Level 10 - Dynamic Tool Gating

```python
"""
Route math to calculator, text to LLM.
"""

if any(c.isdigit() for c in input_text):
    agent.use_tools("calculator")

print(input_text)
```

### Level 12 - Full Adaptive Mode

```python
"""
Adaptive reasoning agent.
"""

agent.temperature = 0.2
agent.use_tools("web_search", "calculator")

# Compress history
if len(message_history) > 8:
    message_history[:] = message_history[-4:]

# Dynamic routing
if "http" in input_text:
    agent.tool_choice = "web_search"

print(f"Solve carefully:\n{input_text}")
```

## File Location

Place your `prompt.py` in:
```
agents/YOUR_AGENT/cortex/prompt.py
```

Or for chat-specific customization:
```
agents/YOUR_AGENT/cortex/chat/prompt.py
```

## Fallback Behavior

If no DSL script is found, the agent uses:
- System message from `DEFAULT_SYSTEM_MESSAGE` environment variable
- User message as-is from the request
- Default conversation history handling
