# Docker Compose Reference

A complete `docker-compose.yaml` for running agent-stem locally with all services.

## Minimal setup (cloud LLM)

No local GPU required. Uses a cloud LLM and a pre-built embedding model.

```yaml
services:
  agent:
    image: sinanozel/agent-stem:latest
    volumes:
      - ./cortex:/app/cortex
    ports:
      - "8000:8000"
    environment:
      - MISTRAL_API_KEY=${MISTRAL_API_KEY:-}
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

## With Ollama (local LLM)

Adds a local Ollama container. The model is baked into the image — no separate `ollama pull` needed.

```yaml
services:
  agent:
    image: sinanozel/agent-stem:latest
    volumes:
      - ./cortex:/app/cortex
    ports:
      - "8000:8000"
    environment:
      - EMBEDDING_SERVER=http://embedding:11434
    depends_on:
      - redis
      - qdrant
      - embedding
      - ollama

  redis:
    image: redis:7-alpine

  qdrant:
    image: qdrant/qdrant:v1.12.1

  embedding:
    image: sinanozel/ollama.0.12.11:all-minilm-33m

  ollama:
    image: sinanozel/ollama.0.12.11:gemma3-270m
    deploy:
      resources:
        reservations:
          memory: 1G
```

```yaml
# cortex/providers/default.yaml
api_base: http://ollama:11434
model: ollama/gemma3:270m
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `DEFAULT_PROVIDER` | — | Name of the provider YAML to use as default (without `.yaml`) |
| `DEFAULT_SYSTEM_MESSAGE` | built-in | System message when `cortex/chat/prompt.py` is absent |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `EMBEDDING_SERVER` | `http://embedding:11434` | Ollama base URL for embeddings |
| `EMBEDDING_MODEL` | `all-minilm:33m` | Embedding model name |
| `QDRANT_HOST` | `qdrant` | Qdrant hostname |
| `QDRANT_PORT` | `6333` | Qdrant port |
| `CONVERSATION_WINDOW_LIMIT` | — | Override context window (tokens). Useful on memory-constrained hardware. |
| `PDF_CHECK_INTERVAL_SECONDS` | `5` | How often to scan for new PDFs |
| `CHUNK_CHECK_INTERVAL_SECONDS` | `10` | How often to scan for new Markdown files |

## Persistent data

Mount volumes to keep Redis and Qdrant data across container restarts:

```yaml
redis:
  image: redis:7-alpine
  volumes:
    - ./data/redis:/data

qdrant:
  image: qdrant/qdrant:v1.12.1
  volumes:
    - ./data/qdrant:/qdrant/storage
```

## Ports

| Port | Service | Description |
|---|---|---|
| `8000` | agent | FastAPI HTTP server (main API) |
| `8501` | agent | Streamlit UI (if enabled) |
| `6333` | qdrant | Qdrant HTTP API |
| `6334` | qdrant | Qdrant gRPC API |
| `6379` | redis | Redis |
