# Quick Start

🤖 agent-stem is a container that runs an AI assistant. You give it a folder called `cortex/` with your configuration and documents. It takes care of the rest.

**What you need to get started:** Docker and an API key from a cloud AI provider (Mistral, Anthropic, or OpenAI all work).

---

## Your first agent — a bakery assistant

Here is a complete, working example. It is a customer-facing chat assistant for a bakery. It knows the menu and allergen information, and has a fixed personality.

### The files

```
bakery-agent/
  docker-compose.yaml
  cortex/
    providers/
      default.yaml        ← which LLM to use
    chat/
      prompt.py           ← the agent's personality and instructions
    library/
      menu.pdf            ← the agent's knowledge base
      allergen-guide.pdf
```

### `cortex/providers/default.yaml`

```yaml
api_base: https://api.mistral.ai
model: mistral/mistral-large-2512
api_key: ${MISTRAL_API_KEY}
```

### `cortex/chat/prompt.py`

```python
"""
You are a friendly assistant for The Flower & Flour Bakery.
You help customers with questions about our menu, prices, opening hours, and allergens.
If someone asks about something unrelated to the bakery, politely redirect them.

Opening hours: Tuesday to Sunday, 8am to 6pm. Closed on Mondays.
Location: 42 Flour Street.
"""

with search(input()):
    print("Customer question: " + input())
```

The text between the triple quotes is the system message — the instructions the AI follows in every conversation. The `with search(input()):` line tells the agent to look up relevant parts of your documents before answering.

### `docker-compose.yaml`

```yaml
services:
  agent:
    image: sinanozel/agent-stem:latest
    ports:
      - "8000:8000"
    volumes:
      - ./cortex:/app/cortex
    environment:
      - MISTRAL_API_KEY=${MISTRAL_API_KEY}
    depends_on:
      - redis
      - qdrant
      - embedding

  redis:
    image: redis:7-alpine

  qdrant:
    image: qdrant/qdrant:v1.12.1

  embedding:
    image: sinanozel/ollama.0.12.11:all-minilm-33m
```

### Start it

```bash
cd bakery-agent
MISTRAL_API_KEY=your-key-here docker compose up
```

### Try it

Open `http://localhost:8000/docs` in a browser to explore the API interactively.

Or, if you are the programming type, go full-on bash:
```bash
curl -X POST http://localhost:8000/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Do you have anything vegan?"}'
```

The agent remembers the conversation. Send a follow-up message with the same `conversation_id` and it will remember what was said:

```bash
curl -X POST http://localhost:8000/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What about something with almonds?", "conversation_id": "chat-1"}'
```

The complete example, including ready-to-use menu and allergen files, lives in [examples/bakery_agent/](../examples/bakery_agent/).

---

## How the documents work

Drop PDF or Markdown files into `cortex/library/`. The agent converts, chunks, embeds, and indexes them automatically in the background — no restart needed when you add new files.

```
cortex/library/
  menu.pdf               ← indexed on first startup
  allergen-guide.pdf     ← indexed on first startup
  spring-specials.pdf    ← add later, picked up automatically
```

The `with search(input()):` in `prompt.py` runs a vector search against these files and adds the most relevant chunks to the message sent to the AI. If you remove the search block, the agent still works — it just won't look things up.

To keep documents in separate groups (for searching one at a time):

```
cortex/library/
  menu/
    current-menu.pdf
    specials.pdf
  policies/
    allergens.pdf
    delivery.pdf
```

Then in `prompt.py`:

```python
with search(input(), collection="menu"):
    print("Customer question: " + input())
```

---

## Workflows — when you need a command, not a conversation

Sometimes you do not need an agent or an assistant, but a simpler workflow: send some text in, get a structured result out. For this, create a YAML file under `cortex/workflows/`. Each file becomes a `POST` endpoint automatically on the next restart.

**Example: summarize text**

```yaml
# cortex/workflows/summarize.yaml
name: summarize
path: /v1/summarize
description: Summarizes the given text concisely.

output_schema:
  type: string

execution:
  type: prompt
  prompt: |
    Summarize the following text in two sentences or less.
```

Call it:

```bash
curl -X POST http://localhost:8000/v1/summarize \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Long article text here..."}]}'
```

**Example: extract structured data**

```yaml
# cortex/workflows/extract-order.yaml
name: extract_order
path: /v1/extract-order
description: Extracts order details from a customer message.

output_schema:
  type: object
  properties:
    item:
      type: string
    quantity:
      type: integer
    special_requests:
      type: string
  required: [item, quantity]

execution:
  type: prompt
  prompt: |
    Extract the order details from the customer message and return JSON.
```

When `output_schema` is an object, the agent validates that the AI returned valid JSON before sending it back. You get structured data you can use directly.

---

## Other LLM providers

Swap the contents of `cortex/providers/default.yaml` to use a different model. No other changes needed.

```yaml
# Anthropic
model: anthropic/claude-haiku-4-5-20251001
api_key: ${ANTHROPIC_API_KEY}
```

```yaml
# Local Ollama (no API key needed)
api_base: http://ollama:11434
model: ollama/gemma3:4b
```

```yaml
# Local llama.cpp
api_base: http://localhost:8080/v1
model: openai/your-model-name
api_key: dummy
timeout: 150
```

See [Model Providers](model_providers.md) for the full reference.

---

## What's next

- [Model Providers](model_providers.md) — all provider options, including local models
- [Evaluation DSL](eval_dsl.md) — write automated test cases for your agent
- [For the DevOps](for-devops.md) — Kubernetes, Helm, scaling, secrets management
- [examples/](../examples/) — all runnable examples with Helm values
