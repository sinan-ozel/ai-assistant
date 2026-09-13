# Test Environment: Self-Hosted LLM

This test environment validates the API with a self-hosted LLM provider (e.g., llama.cpp running on a VPN or local network).
The environment also runs standard OpenAPI tests.

Teh environment runs a Redis and a Qdrant server to work with the agent.

## Prerequisites

- Docker and Docker Compose installed
- A self-hosted llama.cpp server accessible from your network
- Network access to the llama.cpp server

## Setup

1. **Create the `.env` file** in this directory:
   ```bash
   cp .env.example .env
   ```

2. **Configure your llama.cpp server address** in the `.env` file:
   ```
   LLAMA_CPP_HOST=http://your-llama-cpp-server-ip:8080/v1
   ```
   Example: `LLAMA_CPP_HOST=http://10.8.0.103:8080/v1`

3. **Never commit the `.env` file** - it contains network configuration and is already in `.gitignore`

4. **Ensure your llama.cpp server is running** and the `/v1/models` endpoint is accessible:
   ```bash
   curl http://your-llama-cpp-server-ip:8080/v1/models
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
