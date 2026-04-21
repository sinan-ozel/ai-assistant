# agent-stem

🤖 A lightweight AI agent framework. Run locally with 🐳 Docker. Deploy at
scale with ☸️ Kubernetes.

## What is it?

agent-stem is a container-first framework for building AI assistants and
agents. You configure your agent by mounting a single directory (`cortex/`)
into the container.

**The minimum you need to know: Docker.**

## Quickstart - "Talk to your documents" implementation

```
cortex/            ← mount this into the container
  providers/
    default.yaml   ← which LLM to use
  chat/
    prompt.py      ← (optional) system message + agentic logic
  library/         ← (optional) PDFs/Markdown for RAG
  workflows/       ← (optional) YAML-defined API endpoints
```

`default.yaml` may be:

=== "Mistral (cloud)"

    ```yaml
    # cortex/providers/default.yaml
    api_base: https://api.mistral.ai
    model: mistral/mistral-large-2512
    api_key: ${MISTRAL_API_KEY}
    ```

=== "Ollama (local)"

    ```yaml
    # cortex/providers/default.yaml
    api_base: http://ollama:11434
    model: ollama/gemma3:270m
    ```

=== "Anthropic"

    ```yaml
    # cortex/providers/default.yaml
    model: anthropic/claude-haiku-4-5-20251001
    api_key: ${ANTHROPIC_API_KEY}
    ```

Here is what `docker-compose.yaml` looks like:

```
services:
  embedding-test:
    image: sinanozel/ollama.0.12.11:all-minilm-33m
    container_name: embedding-test-local-llm
    networks:
      - ai-assistant-network

  app:
    image: sinanozel/ai-assistant:0.1.0
    networks:
      - ai-assistant-network
    volumes:
      - ./cortex:/app/cortex    ← this is you plugging in the brain you control.
```

Then run:

```bash
docker compose up
```

Your agent is live at `http://localhost:8501`, for personal use and visual testing.
The APIs are available at: `http://localhost:8000/`.
Interactive API docs at `http://localhost:8000/docs`.

## Key features

| Feature | Description |
|---|---|
| **Agent chat** | Stateful conversation with per-user history stored in Redis |
| **RAG** | Drop PDFs into `cortex/library/` — they are chunked and indexed automatically |
| **Workflows** | YAML-defined POST endpoints for structured LLM tasks |
| **Evaluation** | Write test cases in plain Python; run them via HTTP |
| **Any LLM** | OpenAI, Anthropic, Mistral, Ollama, llama.cpp — anything LiteLLM supports |

## Production use

It is tested with Redis and Qdrant, and written to be deployed _in parallel_
in Kuberenetes environments.

## Next steps

- [Quick Start](getting-started/quickstart.md) — up and running in five minutes
- [Model Providers](model_providers.md) — configure your LLM backend
- [Agent Prompt DSL](configuration/prompt-dsl.md) — customise your agent's behaviour
- [Document Library](configuration/library.md) — add RAG to your agent
- [Workflows](configuration/workflows.md) — create structured LLM endpoints
