
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


## This is how you configure your agent

Your agent is configured by mounting a `cortex/` directory into the container.
The minimum setup is a single provider YAML file:

```
cortex/
  providers/
    default.yaml
  chat/
    prompt.py       ← optional: system message + DSL
  library/          ← optional: documents for RAG
  workflows/        ← optional: workflow endpoint definitions
```

**`cortex/providers/default.yaml`** — pick your LLM backend:

```yaml
# Mistral cloud
api_base: https://api.mistral.ai
model: mistral/mistral-large-2512
api_key: ${MISTRAL_API_KEY}
```

```yaml
# Ollama (local)
api_base: http://ollama:11434
model: ollama/gemma3:270m
```

```yaml
# Anthropic
model: anthropic/claude-sonnet-4-5
api_key: ${ANTHROPIC_API_KEY}
```

**`cortex/chat/prompt.py`** — the module-level docstring becomes the system message:

```python
"""
You are a helpful assistant called "Son of Anton".
You specialize in debugging code and finding low-cost hamburgers.
"""

# DSL: inject retrieval results into context
with Search(input())
    print(input())
```

## This is where you put your documents

Place PDFs or Markdown files under `cortex/library/`. They are automatically
converted, chunked, embedded, and stored in the vector database at startup.
Use subfolders to organise documents into named collections:

```
cortex/
  library/
    shelf1/
      my-book.pdf
    shelf2/
      another-document.pdf
```

Files in `shelf1/` become collection `shelf1` in the vector store.
Search them from `prompt.py`:

```python
# Search all collections
with Search(input())
    print(input())

# Search a specific collection
results = Search(input(), "shelf1")

with Search(input(), "shelf1")
    print(input())
```

## If desired, create basic "workflows"

Workflows are streaming POST endpoints that do a specific task using an LLM.
Each YAML file under `cortex/workflows/` becomes a registered endpoint at startup:

```yaml
# cortex/workflows/summarize_text.yaml
name: summarize_text
path: /v1/summarize-text
description: Summarizes the given text into a concise summary.

output_schema:
  type: string

execution:
  type: prompt
  prompt: |
    Clean up and summarize the user message in less than 50 words.
```

For structured JSON output:

```yaml
name: extract_book_metadata
path: /v1/extract-book-metadata
description: Extracts book metadata from a cover image.
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
    Extract the book metadata from this cover image.
```

Note that this one would require you to place a provider called vision under the folder providers, i.e. `/cortex/

## This is how you run your assistant (locally, for testing or for personal use)

```yaml
# docker-compose.yaml
services:
  agent:
    image: sinanozel/agent-stem:latest
    volumes:
      - ./cortex:/app/cortex
    ports:
      - "8000:8000"
    environment:
      - MISTRAL_API_KEY=${MISTRAL_API_KEY}
    depends_on:
      - redis
      - qdrant

  redis:
    image: redis:7-alpine

  qdrant:
    image: qdrant/qdrant:v1.12.1

  embedding:
    image: sinanozel/ollama.0.12.11:all-minilm-33m
```

```bash
docker compose up
# Agent is available at http://localhost:8000
# Interactive API docs at http://localhost:8000/docs
```

## This is how you run the same assistant in production

```yaml
# values.yaml (Helm)
replicaCount: 3

image:
  repository: sinanozel/agent-stem
  tag: "0.1.0"

env:
  - name: MISTRAL_API_KEY
    valueFrom:
      secretKeyRef:
        name: llm-secrets
        key: mistral-api-key

cortex:
  # Mount your cortex as a ConfigMap or PVC
  configMapName: my-agent-cortex
```

```bash
helm install my-agent ./charts/agent-stem -f values.yaml
```


# Features

## Workflows

Declarative YAML-defined POST endpoints. Each file in `cortex/workflows/` is auto-discovered
and registered as an endpoint. Supports text and structured JSON output, image input, streaming,
and built-in evaluation cases. See `agent_stem/src/startup/WORKFLOWS.md` for full reference.

## Agent Chat

Stateful conversation endpoint at `POST /v1/agent/chat`. Maintains per-user, per-conversation
message history in Redis. Context is automatically trimmed to fit the provider's context window.
Customize via `cortex/chat/prompt.py`. See `agent_stem/default/endpoints/public/README.md`.

## Retrieval (RAG)

Drop PDFs or Markdown into `cortex/library/`. Two background pipelines run automatically:
PDF → Markdown (with OCR fallback), then Markdown → chunks → embeddings → vector store.
Supports Qdrant (default) and LanceDB (fallback). Search from `prompt.py` using the `Search()`
DSL function. See `agent_stem/src/startup/DOCUMENT_PIPELINE.md` and `SEARCH.md`.

## Tools

This is in planning. It will implement tools as MCP with streaming HTTP with newline-delimited JSON.
I may include some other format as well, such as OpenAPI.

# Bug Reports

You do not need development experience to make a bug report! I aimed this at
both hobbyists and professionals.

Feel free to go to GitHub and open an issue. Here is what I am expecting:
1. Your `cortex/` folder, with its contents - or at least, the relevant part.
2. What you expected to see.
3. What you got instead.
This would allow me to replicate the issue and fix.

# Developement & Contribution

To contribute, you need github, docker and an LLM.
1. Clone
2. Branch out
3. Under `test_agents`, write an agent that will test the outcome you want.
4. Note that this agent will need to call an LLM to be tested. Consider Mistral, Anthropic, or locally-hosted LLMS, examples exist.
5. If you want to use Claude to write, commands are included, plase use them. Please review your test agent thoroughly before prompting Claude Code.
6. After all tests are passing, use the VS Code tasks to reformat and lint. (You do not actually need to use VS Code, the commands are all docker)
7. Push and open a pull request.

You probably can pull this off with a Windows computer, too, but you do need Docker.

## Testing Harness

Integration tests are run via VS Code tasks in `.vscode/tasks.json`. Each test pairs a
**test agent** (a `cortex/` configuration under `test_agents/`) with a **test environment**
(a `docker-compose.yaml` under `test_environments/`). Run **Run the Pipeline** from the VS Code
task menu to execute lint + unit tests + all integration tests in sequence.

See `TESTING.md` for the full matrix of test agents, environments, and what each covers.

# Future Plans

## MCP Support

I am looking into how I want to develop this. I could give a way for
MCP servers to be registered, or I could put a folder called `tools/` under
`cortex/`, or I could register "workflows" as MCP tools, or a combination of both

No matter which direction I go, the interface is going to be intuitive,
something like the following:
```
"""You are an amazing agent. <3"""

with Toolbox("toolbox_a"):
      print("Use the tools to respond to the questions.")
```

I am also thinking of separating the tools into a two-stage

## More complex structure under `agent/`

Right now, `agent/chat.py` works almost like a DSL: You manage the prompt,
passively inject RAG, and that's it. (Under the hood, there is conversation
memory, but not much more.)

I am planing to extend the DSL to include multiple LLM calls.

## Better Memory and Context Management
Currently, conversation memory is fitted in the most basic way possible.
The plan is to automate summarization, triggered by how long the context window
is set.

## Loops
Get the agent to work on a trigger, something like `cronjob`, and run
a few tasks - maybe even a task list.
