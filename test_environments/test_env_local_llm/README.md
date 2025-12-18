# Test Environment: Gemma3:270M

This test environment validates the API with a Gemma3-270M model running in an Ollama container.

## Overview

This test environment includes:
- Redis for caching
- Qdrant for vector storage
- Embedding service (all-minilm-33m)
- **Ollama server with gemma3-270m model** (sinanozel/ollama.0.12.11:gemma3-270m)
- The application under test
- Test runner

## Running the Tests

From the workspace root, run:

```bash
docker compose -f test_environments/test_env_gemma3_270m/docker-compose.yaml \
  --project-directory test_environments/test_env_gemma3_270m \
  up --build --abort-on-container-exit --exit-code-from tests
```

Or use the VS Code task (after adding it to tasks.json):
- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Linux/Windows)
- Select "Tasks: Run Task"
- Choose "Run Tests (Gemma3-270M)"

## What It Tests

- Provider discovery (gemma3-270m should be discovered)
- Provider context window endpoint
- All standard API endpoints with a local LLM model

## Model Specifications

- **Model**: Gemma3-270M
- **Size**: ~2.5GB
- **Parameters**: 270 million
- **Use case**: Lightweight model suitable for CPU inference
- **Provider**: Ollama running in Docker container
