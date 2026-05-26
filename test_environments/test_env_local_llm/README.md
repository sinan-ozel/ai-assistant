# Test Environment: Local LLM

This test environment validates the API with fully local LLM inference — no external network access required.
The environment also runs standard OpenAPI tests.

The environment runs Redis, Qdrant, a llama.cpp server (qwen3-0.6b), and an Ollama server (gemma3-270m). Embedding runs in-process via fastembed (all-MiniLM-L6-v2).

## Running the Tests

From the workspace root, run:

```bash
docker compose -f test_environments/test_env_local_llm/docker-compose.yaml \
  up --build --exit-code-from tests
```

Set `AGENT_FOLDER` to the agent you want to test and `TEST_FOLDER` to the pytest folder.
See `.vscode/tasks.json` for examples.
