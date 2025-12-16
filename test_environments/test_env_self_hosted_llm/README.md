# Test Environment: Self-Hosted LLM

This test environment validates the API with a self-hosted LLM provider (e.g., Ollama running on a VPN or local network).

## Prerequisites

- Docker and Docker Compose installed
- A self-hosted Ollama server accessible from your network
- Network access to the Ollama server

## Setup

1. **Create the `.env` file** in this directory:
   ```bash
   cp .env.example .env
   ```

2. **Configure your Ollama server address** in the `.env` file:
   ```
   OLLAMA_HOST=your-ollama-server-ip:11434
   ```
   Example: `OLLAMA_HOST=10.8.0.103:11434`

3. **Never commit the `.env` file** - it contains network configuration and is already in `.gitignore`

4. **Ensure your Ollama server is running** and the `/api/tags` endpoint is accessible:
   ```bash
   curl http://your-ollama-server-ip:11434/api/tags
   ```

## Running the Tests

From the workspace root, run:

```bash
docker compose -f test_environments/test_env_self_hosted_llm/docker-compose.yaml \
  --project-directory test_environments/test_env_self_hosted_llm \
  up --build --abort-on-container-exit --exit-code-from tests
```

Or use the VS Code task:
- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Linux/Windows)
- Select "Tasks: Run Task"
- Choose "Run Tests (Self-Hosted LLM)"

## Test Behavior

- **OLLAMA_HOST not set**: Tests will be skipped with a message to configure the environment variable
- **Ollama server unreachable**: Tests will be skipped with a message indicating the server is not reachable
- **Ollama server available**: Tests will run normally

This ensures tests don't fail when the self-hosted infrastructure is temporarily unavailable.

## What This Tests

This environment validates:
- API endpoints work correctly with a self-hosted LLM provider
- Provider discovery successfully finds and validates the self-hosted provider
- The `/private/v1/providers` endpoint returns correct provider information
- No external API keys are required for self-hosted providers

## Test Files

- `conftest.py` - Pytest fixtures including Ollama server availability check
- `test_providers.py` - Provider-specific validation

## Environment Details

This test environment:
- **Includes**: Agent STEM application, Redis, Qdrant, Embedding service
- **Requires**: External self-hosted Ollama server (configured via OLLAMA_HOST)
- **Custom providers**: Mounted from `./cortex` directory
