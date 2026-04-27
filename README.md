
# Introduction

🤖 This is a framework for creating very lightweight AI agents, hence the word
assistant. Write as a hobbyist and run locally using 🐳 Docker, or deploy in
parallel in production using ⛵ Helm charts on ☸️ Kubernetes clusters.

Design Principles:
1. Test locally with 🐳 Docker
2. Deploy in parallel with ☸️ Kubernetes
3. Only knowledge needed to start: Docker.
4. To get more advanced: YAML files, basic Python
5. Underneath, it's actually Python, so write your agentic flow as you see fit.
6. Evaluation is a first-class citizen in this: the framework lets you write your evaluation.
7. Locally-hosted or self-hosted models are also a first-class citizen: this has been developed and tested with small models working on a very old machine.

## The cortex is your application

The `cortex/` directory is not configuration — it **is** the application. Choosing a model, writing the system prompt, defining workflows, loading documents: these are application-level decisions made during development and evaluation, not deployment decisions made by infrastructure teams.

This means the cortex travels with the code, not with the cluster. Docker Compose mounts it as a local directory; Kubernetes delivers it as a ConfigMap. The container image, Redis, Qdrant, and the model servers are infrastructure — interchangeable and replaceable. The cortex is what makes your agent *your* agent.

---

## Quick start — a working agent in two minutes

Create one file:

```yaml
# cortex/providers/default.yaml
api_base: https://api.mistral.ai
model: mistral/mistral-large-2512
api_key: ${MISTRAL_API_KEY}
```

Then run:

```bash
MISTRAL_API_KEY=your-key-here \
  docker compose -f agent_stem/docker-compose.default.yaml up
```

Your agent is live. The API is at `http://localhost:8000` and interactive docs at `http://localhost:8000/docs`.

Send a message:

```bash
curl -X POST http://localhost:8000/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

Other supported LLM backends — swap into `default.yaml`:

```yaml
# Anthropic
model: anthropic/claude-haiku-4-5-20251001
api_key: ${ANTHROPIC_API_KEY}
```

```yaml
# Local Ollama
api_base: http://ollama:11434
model: ollama/gemma3:270m
```

```yaml
# Local llama.cpp (OpenAI-compatible server)
api_base: http://localhost:8080/v1
model: openai/gemma4:e2b
api_key: dummy
timeout: 150
```

Anything [LiteLLM supports](https://docs.litellm.ai/docs/providers) works here — just set `model` and `api_base` accordingly.

---

## Give your agent a personality

Add `cortex/chat/prompt.py`. The module-level docstring becomes the system message:

```python
# cortex/chat/prompt.py
"""
You are a helpful assistant called "Aria".
You are friendly and concise. When you don't know something, say so.
"""

print(input_text)
```

That's all you need. The `print(input_text)` passes the user's message through unchanged. Restart the container and the new system message is active.

---

## Talk to your documents (RAG)

Drop PDF or Markdown files into `cortex/library/`. They are automatically converted, chunked, embedded, and indexed into the vector database. Use subfolders as collection names:

```
cortex/
  library/
    product-docs/
      manual.pdf
    policies/
      handbook.pdf
```

Then in `prompt.py`, inject the relevant chunks into the conversation:

```python
"""
You are a support assistant. Answer using the provided documentation.
If the answer is not in the documents, say so.
"""

with search(input()):
    print("User question: " + input())
```

`search(input())` runs a vector search and prints the matching chunks into the user message before the question. The LLM sees both.

To restrict search to one collection:

```python
with search(input(), collection="product-docs", top_k=3):
    print("User question: " + input())
```

No code changes needed when you add new documents — the pipeline picks them up automatically on the next poll cycle.

---

## Create typed API endpoints (Workflows)

Each YAML file in `cortex/workflows/` becomes a `POST` endpoint at startup:

```yaml
# cortex/workflows/summarize.yaml
name: summarize
path: /v1/summarize
description: Summarize text in under 50 words.

output_schema:
  type: string

execution:
  type: prompt
  prompt: |
    Summarize the following text in under 50 words.
```

For structured JSON output:

```yaml
# cortex/workflows/extract-book.yaml
name: extract_book_metadata
path: /v1/extract-book-metadata
description: Extract book title and author from a cover image.
provider: vision

input_requirements:
  content_types: [image]

output_schema:
  type: object
  properties:
    title:
      type: string
    author:
      type: string
  required: [title, author]

execution:
  type: prompt
  prompt: |
    Extract the book title and author from this cover image.
```

The endpoint validates the LLM's JSON response against the schema before returning it.

---

## Architecture

This section is for developers who want to understand or contribute to the framework.

### Directory layout

```
agent_stem/              ← the container image source
  default/endpoints/     ← auto-discovered HTTP endpoint modules
  src/
    common/              ← shared logic (search, DSL, chunking)
    startup/             ← provider, workflow, and pipeline startup code
test_agents/             ← integration test fixtures (one cortex per agent)
test_environments/       ← docker-compose files for each test scenario
examples/                ← runnable examples with helm values
docs/                    ← user documentation (MkDocs)
```

### HTTP endpoints

Three public endpoints are registered out of the box:

| Endpoint | Standard | Description |
|---|---|---|
| `POST /v1/chat/completions` | OpenAI Chat API | Stateless LLM proxy, OpenAI-compatible |
| `POST /v1/api/generate` | Ollama Generate API | Stateless LLM proxy, Ollama-compatible |
| `POST /v1/agent/chat` | Custom | Stateful conversation with Redis history |

Private endpoints (path starts with `/private/`) are for internal use: health, search, books list, provider status, evaluation.

All endpoints are auto-discovered from Python files under `default/endpoints/`. Each file exports a `handler` async function and a `spec` dict describing the route in OpenAPI terms. Adding a new endpoint is as simple as dropping a file.

### LLM providers

Provider YAML files in `cortex/providers/` are loaded at startup. Every key in the file is passed as a keyword argument to LiteLLM's `acompletion()`. Environment variables are substituted with `${VAR_NAME}` syntax.

Selection priority at startup:
1. `cortex/providers/default.yaml` (crashes on failure)
2. `DEFAULT_PROVIDER` env var matching a file in `cortex/providers/` (crashes on failure)
3. The only file in `cortex/providers/` if exactly one exists
4. Built-in Mistral fallback requiring `MISTRAL_API_KEY` (runs in no-LLM mode if key is absent)

Named providers (non-default) are referenced by name from workflow YAML files using the `provider:` key. They are validated at request time, not startup.

### Prompt DSL

`cortex/chat/prompt.py` is executed on every `/v1/agent/chat` request. The runtime injects these globals without any imports:

| Name | Description |
|---|---|
| `input_text` | The current user message |
| `message_history` | Mutable conversation history list |
| `agent` | Config object for overriding model, temperature, streaming, etc. |
| `search` | Context manager for vector search (RAG) |

The module docstring becomes the system prompt. Everything `print()`-ed becomes the user message sent to the LLM (blank lines split output into multiple user message objects).

### Document pipeline

Two background processes run concurrently at startup:

**Stage 1 — PDF pipeline** (polls every 5 s): detects new or changed PDFs under `cortex/library/` by SHA-256 hash, converts them to Markdown using `pymupdf4llm` (with Tesseract OCR fallback for image-based PDFs), and prepends YAML front matter with file metadata and tags derived from the folder path.

**Stage 2 — Chunking pipeline** (polls every 10 s): reads Markdown files, segments them by ATX heading, embeds each chunk via an Ollama-compatible embedding server, and writes chunks to Qdrant (preferred) or LanceDB (fallback). The top-level subfolder under `library/` becomes the collection name.

Both pipelines track state in Redis. A missing Redis connection causes them to silently skip, keeping the API available.

### Context management

On each `/v1/agent/chat` request, the full conversation history is read from Redis, then trimmed to fit the provider's context window before the LLM call. The context window size is queried from LiteLLM at startup (`get_model_info()`), then cached. `CONVERSATION_WINDOW_LIMIT` can cap it below the model's theoretical maximum (useful for VRAM-constrained deployments). The full history is always preserved in Redis — only the LLM call is trimmed.

### Evaluation

Two evaluation mechanisms are available:

**Agent eval DSL** (`cortex/chat/eval.py`): write test cases as plain Python functions. Triggered via `POST /private/v1/agent/evaluate`. Supports regexp checks, embedding similarity, LLM-as-judge, and multi-turn scenarios.

**Workflow evaluation**: inline `evaluation:` blocks in workflow YAML files. Triggered via `POST /private/evaluate{path}`.

---

## Development & Contribution

To contribute:

1. Clone the repo and branch out.
2. Under `test_agents/`, write an agent (a `cortex/` directory) that demonstrates the behaviour you want to test.
3. Under `test_environments/`, select or create a `docker-compose.yaml` for the test scenario.
4. Write integration tests in the test agent's `tests/` directory. Tests call HTTP endpoints — no direct Redis or Qdrant access.
5. Run **Run the Pipeline** from VS Code tasks (lint → unit tests → integration tests).
6. After all tests pass, push and open a pull request.

See `TESTING.md` for the full test matrix.

Do not use `print()` — use the existing logging patterns. Do not install packages outside Docker — all dependencies are managed through the container build. Do not add `try/except` except around HTTP endpoint handlers or to enrich a log message before re-raising.

---

## Future Plans

**MCP / Tools** — tool support is planned. The interface will follow the cortex convention:

```python
"""You are an agent with tools."""

with Toolbox("my-tools"):
    print("Use the tools to answer this: " + input_text)
```

**Extended DSL** — multi-LLM-call flows within a single `prompt.py`, enabling sequential reasoning or routing between models.

**Better memory** — automated summarization of older conversation turns when the context window is full, rather than simple truncation.

**Scheduled triggers** — cron-style agent runs from a `cortex/` task definition.
