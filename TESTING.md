# Testing

Integration tests are run via VS Code tasks defined in `.vscode/tasks.json`. Each test run
pairs a **test agent** (a `cortex/` configuration) with a **test environment** (a
`docker-compose.yaml` that provides infrastructure services).

---

## How to run

From VS Code, open the Command Palette and run **Tasks: Run Task**, then select:

- **Run the Pipeline** — lint + unit tests + all integration tests in sequence.
- **Run Integration Tests: `<agent>` @ `<env>`** — a single agent/environment pair.
- **Run Unit Tests: self_hosted_llm** — unit tests only (`no_agent` against `self_hosted_llm`).

Alternatively, from the terminal:

```bash
AGENT_FOLDER=test_agents/<agent>/cortex \
TEST_FOLDER=test_agents/<agent>/tests \
docker compose -f test_environments/<env>/docker-compose.yaml up --build --exit-code-from tests
```

---

## Test environments

Each environment is a `docker-compose.yaml` under `test_environments/`. The **app** container
is always built from `agent_stem/Dockerfile`. The **tests** container runs `pytest` against it.

| Environment | Redis | Qdrant | Embedding | LLM | Notes |
|---|---|---|---|---|---|
| `test_env_default` | ✓ | ✓ | ✓ (all-minilm:33m) | ✓ (gemma3-270m) | Bridge network. `LOG_LEVEL=DEBUG` on app. Cortex mounted to app only. |
| `test_env_self_hosted_llm` | ✓ | ✓ | ✓ (all-minilm:33m) | external | Host network. Cortex mounted to both app and tests containers. LLM provided by `OLLAMA_HOST`. |
| `test_env_mistral` | ✓ | ✓ | ✓ (all-minilm:33m) | external | Mistral API via `MISTRAL_API_KEY`. `DEFAULT_PROVIDER=mistral-7b`. |
| `test_env_no_llm` | ✓ | ✓ | ✓ (all-minilm:33m) | ✗ | App starts in no-LLM mode. Tests infrastructure and non-LLM paths. |
| `test_env_no_qdrant` | ✓ | ✗ | ✓ (all-minilm:33m) | external | LanceDB fallback active. Cortex mounted to both app and tests containers. |
| `test_env_no_redis` | ✗ | ✓ | ✗ | external | No conversation memory. Embedding points to external server. |
| `test_env_local_llm` | ✓ | ✓ | ✓ (all-minilm:33m) | ✓ (llama.cpp + gemma3-270m) | llama.cpp GPU container + Ollama. Requires CUDA. |
| `test_env_nothing` | ✗ | ✗ | ✗ | ✗ | Bare app only. Tests graceful degradation with no services. |

---

## Test agents

Each agent lives under `test_agents/<name>/` with a `cortex/` configuration and a `tests/` directory.

| Agent | Cortex contents | Test files | What it tests |
|---|---|---|---|
| `no_agent` | `providers/default.yaml` | health, chat, OpenAPI contract, providers | Baseline: no DSL, no library. Unit-level coverage of core endpoints. |
| `agent_with_only_a_system_message` | `chat/prompt.py`, `providers/default.yaml` | health, agent_chat | Agent with a system prompt only (no search, no tools). |
| `agent_with_temperature` | `chat/prompt.py`, `providers/default.yaml` | health, agent_chat | Agent that sets temperature via the DSL `agent` object. |
| `agent_with_search` | `chat/prompt.py`, `providers/default.yaml`, `library/shelf2/lycanthropes-in-eberron.pdf` | health, pipeline, agent_chat | Search-augmented agent. Pipeline test waits for book ingestion; chat test asks a question answerable only from the PDF. |
| `agent_with_collection_search` | `chat/prompt.py`, `providers/default.yaml`, `library/shelf1/city-guide.md`, `library/shelf2/city-guide.md` | health, pipeline, agent_chat | Collection-scoped search using the capitalised `Search` DSL alias. shelf1 and shelf2 contain conflicting facts about a fictional city; the agent uses `Search(input(), "shelf1")` and the test verifies only shelf1 facts appear in the response. |
| `son_of_anton` | `chat/prompt.py`, `chat/advanced_prompt.py`, `chat/evaluation.yaml`, `providers/default.yaml` | health, agent_chat | Named persona agent; tests identity and persona responses. |
| `talk_to_your_documents` | `providers/default.yaml`, `library/shelf1/`, `library/shelf2/` (3 PDFs), `library/.eberron/` (hidden, not ingested) | health, pipeline, search | Full document pipeline: PDF → Markdown → Qdrant → search. Tests conversion, chunking, re-chunking on edit, `/private/v1/books`, and `/private/v1/search`. |
| `text_workflows` | `providers/default.yaml`, `providers/vision.yaml`, `workflows/summarize_text.yaml` | health, OpenAPI contract, providers, summarize_text | Text-only workflow endpoints. |
| `image_workflows` | `providers/vision.yaml`, workflows (book metadata, nutrition, book title), evaluation images | health, OpenAPI contract, providers, image_workflows, evaluation | Vision workflow endpoints and the evaluation pipeline. |
| `incorrect_agent` | `providers/bad_vision.yaml`, a broken workflow | health, providers, evaluation_error | Error handling: bad provider config, evaluation failure paths. |
| `agent_with_eval` | `chat/prompt.py`, `chat/eval.py`, `providers/default.yaml` | evaluate | Python eval DSL: `POST`/`GET`/`DELETE /private/v1/agent/evaluate`. |
| `agent_with_incorrect_eval` | `chat/prompt.py`, `chat/eval.py` (with `expekt()` typo), `providers/default.yaml` | evaluate_error | Verifies that a NameError in a case is caught per-case, recorded as `status: "error"`, and does not prevent other cases from running. |
| `agent_with_tools` | `chat/prompt.py`, `providers/default.yaml` | health, agent_with_tools | Single-phase MCP agent. Calls `call_read_only()` + `wait()` + `llm()` against the `eberron-mcp-server`. Tests health, basic response, tool context, and NDJSON streaming. Requires `test_env_default` (includes `eberron-mcp-server`). |
| `agent_with_tools_advanced` | `chat/prompt.py`, `providers/default.yaml` | health, agent_with_tools_advanced | Two-phase MCP agent. Calls read-only tools first, then all tools, with `notify()` between phases. Tests multi-phase response and that streaming yields multiple intermediate chunks. Requires `test_env_default`. |
| `agent_with_a_system_message_and_prompt_template` | *(no tests yet)* | — | — |
| `agent_with_model_control` | *(no tests yet)* | — | — |

---

## Integration test matrix

Tasks defined in `.vscode/tasks.json` under **Run All Agent Integration Tests**:

| Task | Agent | Environment |
|---|---|---|
| Run Integration Tests: text_workflows @ self_hosted_llm | `text_workflows` | `test_env_self_hosted_llm` |
| Run Integration Tests: image_workflows @ self_hosted_llm | `image_workflows` | `test_env_self_hosted_llm` |
| Run Integration Tests: son_of_anton @ self_hosted_llm | `son_of_anton` | `test_env_self_hosted_llm` |
| Run Integration Tests: talk_to_your_documents @ self_hosted_llm | `talk_to_your_documents` | `test_env_self_hosted_llm` |
| Run Integration Tests: talk_to_your_documents @ no_qdrant | `talk_to_your_documents` | `test_env_no_qdrant` |
| Run Integration Tests: agent_with_only_a_system_message @ default | `agent_with_only_a_system_message` | `test_env_default` |
| Run Integration Tests: agent_with_temperature @ default | `agent_with_temperature` | `test_env_default` |
| Run Integration Tests: agent_with_search @ default | `agent_with_search` | `test_env_default` |
| Run Integration Tests: agent_with_collection_search @ default | `agent_with_collection_search` | `test_env_default` |
| Run Integration Tests: agent_with_eval @ default | `agent_with_eval` | `test_env_default` |
| Run Integration Tests: agent_with_incorrect_eval @ default | `agent_with_incorrect_eval` | `test_env_default` |
| Run Integration Tests: agent_with_tools @ default | `agent_with_tools` | `test_env_default` |
| Run Integration Tests: agent_with_tools_advanced @ default | `agent_with_tools_advanced` | `test_env_default` |

`talk_to_your_documents` is run against two environments to verify that the search layer falls
back correctly from Qdrant to LanceDB when Qdrant is unavailable.

`agent_with_tools` and `agent_with_tools_advanced` both require `test_env_default` because that
environment includes the `eberron-mcp-server` sidecar that the agents connect to via `McpServer`.

---

## Test dependencies (`pytest-depends`)

Tests within a suite declare ordering via `@pytest.mark.depends`. The standard chain is:

```
test_health_endpoint  (name="healthy")
    └── test_agent_chat_basic_response  (name="test_agent_chat_basic_response")
            └── test_agent_chat_search_graceful_no_results
    └── test_books_ingested  (name="test_books_ingested")
            └── test_agent_chat_answers_from_library
```

Pipeline suites (`talk_to_your_documents`, `agent_with_search`, `agent_with_collection_search`)
use `chunk_reset` and (where applicable) `pdf_conversion_reset` fixtures to clear Redis state
and drop Qdrant collections before re-running the ingestion pipeline from scratch.
`agent_with_collection_search` uses only `chunk_reset` because its library contains `.md` files
directly (no PDF conversion step).

---

## DevOps notes

### Embedding server requirements when the document pipeline is active

The document pipeline (PDF → Markdown conversion → chunking → embedding → vector store) uses
the same embedding server as the search path (query embedding at inference time).  When both
run concurrently against a **single Ollama instance with `OLLAMA_NUM_PARALLEL: 1`**, the
pipeline's batch embedding requests monopolise the server, causing search query embedding
requests to time out.

**Consequences in test environments:**

- `test_env_no_qdrant` runs agents that do both document ingestion and live search queries.
  If the environment provisions only one Ollama container, library-chat tests that fire while
  ingestion is still embedding documents will fail with `EmbeddingUnavailableError`.

**Solutions (pick one):**

1. **Dedicated embedding containers** — deploy a separate Ollama instance for the pipeline
   (set `EMBEDDING_BASE_URL` for the pipeline) and a separate one for query embedding.  This
   is the most reliable option: each path gets its own server with no contention.

2. **`OLLAMA_NUM_PARALLEL: N`** — set this env var on the shared Ollama container.  For BERT
   embedding models this enables true batching (`n_seq_max=N`), allowing multiple concurrent
   embedding requests.  It reduces contention but does not eliminate it under heavy load.

The test dependency chain (`healthy` → `test_books_ingested` → library chat tests) ensures
library-chat tests do not start until ingestion is complete, which eliminates the race in
normal sequential runs.  A dedicated embedding server is required only when pipeline ingestion
and search queries must run truly in parallel.
