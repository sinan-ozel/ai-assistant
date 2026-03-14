# Test Environment: No Qdrant

This test environment validates the agent without a Qdrant vector store.
It is used to test that the agent degrades gracefully when Qdrant is unavailable — for example, verifying that the chunking pipeline handles the missing service correctly and that the rest of the API remains functional.

The environment runs a Redis server and an embedding model, but no Qdrant instance.

## Running the Tests

From the workspace root, run:

```bash
docker compose -f test_environments/test_env_no_qdrant/docker-compose.yaml \
  up --build --exit-code-from tests
```

Set `CORTEX_FOLDER` to the agent you want to test and `TEST_FOLDER` to the pytest folder.
See `.vscode/tasks.json` for examples.
