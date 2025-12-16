# Test Environment: Mistral Provider

This test environment validates the API with a single LLM provider (Mistral).

## Prerequisites

- Docker and Docker Compose installed
- A valid Mistral API key

## Setup

1. **Create the `.env` file** in this directory:
   ```bash
   cp .env.example .env
   ```

2. **Add your Mistral API key** to the `.env` file:
   ```
   MISTRAL_API_KEY=your-actual-mistral-api-key-here
   ```

3. **Never commit the `.env` file** - it contains secrets and is already in `.gitignore`

## Running the Tests

From the workspace root, run:

```bash
docker compose -f test_environments/test_env_mistral/docker-compose.yaml \
  --project-directory test_environments/test_env_mistral \
  up --build --abort-on-container-exit --exit-code-from tests
```

Or use the VS Code task:
- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Linux/Windows)
- Select "Tasks: Run Task"
- Choose "Run Tests (Mistral)"

## What This Tests

This environment validates:
- API endpoints work correctly with a configured LLM provider
- Provider discovery successfully finds and validates the Mistral provider
- The `/private/v1/providers` endpoint returns correct provider information

## Test Files

- `test_health_endpoint.py` - Basic health check
- `test_openapi_responses.py` - Validates OpenAPI spec compliance and response examples
- `test_providers.py` - Provider-specific validation

## Environment Details

This test environment:
- **Includes**: Agent STEM application with Mistral provider configuration
- **Excludes**: Redis, Qdrant, Embedding service (not needed for basic API tests)
