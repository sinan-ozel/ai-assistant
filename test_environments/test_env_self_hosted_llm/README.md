# Test Environment: Self-Hosted LLM

This test environment validates the API with a self-hosted LLM provider (e.g., Ollama running on a VPN or local network).
The environment also runs standard OpenAPI tests.

Teh environment runs a Redis and a Qdrant server to work with the agent.

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

Set up `AGENT_FOLDER` to the agent you want to test, and `TEST_FOLDER` to the pytest folder.
See .vscode/tasks.json for examples.
