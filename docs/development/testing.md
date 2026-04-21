# Testing

Integration tests are run via VS Code tasks. Each test pairs a **test agent** (a `cortex/`
configuration under `test_agents/`) with a **test environment** (a `docker-compose.yaml`
under `test_environments/`).

## Running tests

From VS Code: open the Command Palette → **Tasks: Run Task**, then choose:

- **Run the Pipeline** — lint + unit tests + all integration tests in sequence.
- **Run Integration Tests: `<agent>` @ `<env>`** — a single agent/environment pair.

From the terminal:

```bash
AGENT_FOLDER=test_agents/<agent>/cortex \
TEST_FOLDER=test_agents/<agent>/tests \
docker compose -f test_environments/<env>/docker-compose.yaml up --build --exit-code-from tests
```

## Test environments

| Environment | LLM | Notes |
|---|---|---|
| `test_env_default` | gemma3-270m (Ollama bundled) | Bridge network. Recommended for local development. |
| `test_env_self_hosted_llm` | external (`OLLAMA_HOST`) | Host network. Requires a running Ollama server. |
| `test_env_mistral` | Mistral API | Requires `MISTRAL_API_KEY`. |
| `test_env_no_llm` | none | Tests infrastructure and non-LLM paths. |
| `test_env_no_qdrant` | external | LanceDB fallback active. |
| `test_env_no_redis` | external | No conversation memory. |
| `test_env_local_llm` | llama.cpp + CUDA | Requires NVIDIA GPU. |
| `test_env_nothing` | none | Bare app only. Tests graceful degradation. |

## Test agents

| Agent | What it tests |
|---|---|
| `no_agent` | Core endpoints: health, chat completions, OpenAPI contract, providers |
| `agent_with_only_a_system_message` | System prompt only |
| `agent_with_temperature` | Temperature control via DSL |
| `agent_with_search` | RAG search from `prompt.py` |
| `agent_with_collection_search` | Collection-scoped search |
| `son_of_anton` | Named persona agent |
| `talk_to_your_documents` | Full document pipeline: PDF → chunks → Qdrant → search |
| `text_workflows` | Text workflow endpoints |
| `image_workflows` | Vision workflow endpoints and evaluation |
| `agent_with_eval` | Agent evaluation DSL |
| `agent_with_incorrect_eval` | Error handling in evaluation |

See `TESTING.md` in the repository root for the full matrix.

## Writing a new test agent

1. Create `test_agents/<name>/cortex/` with a valid provider YAML.
2. Create `test_agents/<name>/tests/` with pytest files.
3. Add a task to `.vscode/tasks.json` following the existing pattern.
4. Add the task to **Run All Agent Integration Tests** → `dependsOn`.
