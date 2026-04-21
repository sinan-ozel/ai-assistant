# The `cortex/` Directory

The `cortex/` directory is the single point of customisation for your agent. Mount it into
the container and the framework discovers everything inside at startup. No rebuilds required.

## Structure

```
cortex/
├── providers/                 ← required: at least one LLM provider
│   ├── default.yaml           ← default provider (used by all endpoints)
│   ├── vision.yaml            ← named provider (used by workflows that declare it)
│   └── coding.yaml
│
├── chat/                      ← optional: agent customisation
│   ├── prompt.py              ← system message + agentic DSL
│   ├── eval.py                ← evaluation test cases
│   └── advanced_prompt.py     ← advanced DSL patterns (not auto-loaded)
│
├── library/                   ← optional: documents for RAG
│   ├── shelf1/
│   │   └── my-book.pdf
│   └── shelf2/
│       └── another-doc.md
│
└── workflows/                 ← optional: YAML-defined API endpoints
    ├── summarize_text.yaml
    └── extract_metadata.yaml
```

## Mounting the cortex

=== "Docker Compose"

    ```yaml
    services:
      agent:
        image: sinanozel/agent-stem:latest
        volumes:
          - ./cortex:/app/cortex
    ```

=== "Docker run"

    ```bash
    docker run -v "$(pwd)/cortex:/app/cortex" sinanozel/agent-stem:latest
    ```

=== "Kubernetes"

    Mount a ConfigMap or PVC at `/app/cortex`. See [Kubernetes & Helm](../getting-started/kubernetes.md).

## What gets discovered at startup

| Path | Discovered by | What happens |
|---|---|---|
| `providers/*.yaml` | `startup/providers.py` | LLM backends are registered and validated |
| `chat/prompt.py` | `default/endpoints/public/agent_chat.py` | Loaded on first agent chat request |
| `chat/eval.py` | `default/endpoints/private/evaluate.py` | Loaded when evaluation is triggered |
| `library/**/*.pdf` | `startup/pdf_pipeline.py` | Converted to Markdown (polling loop) |
| `library/**/*.md` | `startup/chunking_pipeline.py` | Chunked and embedded (polling loop) |
| `workflows/*.yaml` | `startup/workflows.py` | Registered as POST endpoints |

Files and directories whose names start with `.` are ignored everywhere (hidden files,
hidden subdirectories).

## Minimal cortex

The absolute minimum is one provider file:

```
cortex/
└── providers/
    └── default.yaml
```

Everything else is optional. Without `chat/prompt.py`, a built-in default system message
is used. Without `library/`, the agent runs without RAG. Without `workflows/`, only the
built-in endpoints are available.
