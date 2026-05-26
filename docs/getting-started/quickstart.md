# Quick Start

Get an agent running in five minutes.

## Prerequisites

- Docker and Docker Compose
- An LLM API key (Mistral, OpenAI, Anthropic) **or** a locally-running Ollama server

## 1. Create your cortex directory

```bash
mkdir -p my-agent/cortex/providers
```

## 2. Configure a provider

=== "Mistral"

    ```bash
    cat > my-agent/cortex/providers/default.yaml << 'EOF'
    api_base: https://api.mistral.ai
    model: mistral/mistral-large-2512
    api_key: ${MISTRAL_API_KEY}
    EOF
    ```

    Set your key:
    ```bash
    export MISTRAL_API_KEY=your-key-here
    ```

=== "OpenAI"

    ```bash
    cat > my-agent/cortex/providers/default.yaml << 'EOF'
    model: gpt-4o
    api_key: ${OPENAI_API_KEY}
    EOF
    ```

    Set your key:
    ```bash
    export OPENAI_API_KEY=your-key-here
    ```

=== "Ollama (local)"

    Requires Ollama running with a model pulled (`ollama pull gemma3`).

    ```bash
    cat > my-agent/cortex/providers/default.yaml << 'EOF'
    api_base: http://host.docker.internal:11434
    model: ollama/gemma3
    EOF
    ```

## 3. Create a docker-compose.yaml

```yaml
# my-agent/docker-compose.yaml
services:
  agent:
    image: sinanozel/ai-assistant:0.1.0
    volumes:
      - ./cortex:/app/cortex
    ports:
      - "8000:8000"
    environment:
      - MISTRAL_API_KEY=${MISTRAL_API_KEY:-}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
    depends_on:
      - redis
      - qdrant

  redis:
    image: redis:7-alpine

  qdrant:
    image: qdrant/qdrant:v1.12.1
```

## 4. Start

```bash
cd my-agent
docker compose up
```

## 5. Chat

```bash
curl -X POST http://localhost:8000/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! What can you do?"}'
```

Or open `http://localhost:8000/docs` in your browser for the interactive Swagger UI.

## What's next?

- [Add a system message](../configuration/prompt-dsl.md) to give your agent a persona
- [Add documents](../configuration/library.md) for retrieval-augmented generation
- [Create workflows](../configuration/workflows.md) for structured LLM endpoints
- [Deploy on Kubernetes](kubernetes.md) when you're ready to scale
