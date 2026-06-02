# Environment Variables

All variables consumed by the application. Groups below reflect where each variable is primarily read.

---

## LLM / Provider

| Variable | Default | Description |
|---|---|---|
| `DEFAULT_PROVIDER` | _(none)_ | Name of the default LLM provider as defined in `cortex/providers/`. When unset the built-in Mistral fallback is attempted. |
| `MISTRAL_API_KEY` | _(none — required for built-in fallback)_ | API key for the Mistral hosted service. Used by the built-in fallback provider and any custom provider YAML that references `${MISTRAL_API_KEY}`. |
| `ANTHROPIC_API_KEY` | _(none)_ | API key for the Anthropic hosted service. Required when using an Anthropic-based provider. |
| `OLLAMA_HOST` | _(none)_ | Base URL of an external Ollama server (e.g. `http://host:11434`). Required when using a provider that points at a remote Ollama instance. |
| `LLAMA_CPP_HOST` | _(none)_ | Base URL of an external llama.cpp server (e.g. `http://host:8080/v1`). Required when using a provider that points at a remote llama.cpp instance. |
| `CONVERSATION_WINDOW_LIMIT` | _(no limit)_ | Maximum token count for the conversation context window. Useful when VRAM is the binding constraint rather than the model's theoretical maximum. |
| `DEFAULT_SYSTEM_MESSAGE` | `""` | Fallback system message used when the cortex does not provide one. |

---

## Redis

| Variable | Default | Description |
|---|---|---|
| `REDIS_HOST` | `redis` | Hostname of the Redis server. Read by the `synced-memory` package. |
| `REDIS_PORT` | `6379` | Port of the Redis server. Read by the `synced-memory` package. |

---

## Qdrant (vector search)

| Variable | Default | Description |
|---|---|---|
| `QDRANT_HOST` | `qdrant` | Hostname of the Qdrant server. When unreachable the system falls back to LanceDB. |
| `QDRANT_PORT` | `6333` | gRPC/HTTP port of the Qdrant server. |
| `QDRANT_COLLECTION` | `library` | Name of the Qdrant collection used for document storage. |

---

## LanceDB (fallback vector store)

| Variable | Default | Description |
|---|---|---|
| `LANCEDB_PATH` | `/app/data/lancedb` | Filesystem path where LanceDB stores its data inside the container. |
| `LANCEDB_TABLE` | `library` | LanceDB table name used for document storage. |

---

## Embedding

| Variable | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `nomic-ai/nomic-embed-text-v1.5` | fastembed model name. Runs in-process — no external server required. |

---

## PDF / chunking pipelines

| Variable | Default | Description |
|---|---|---|
| `PDF_CHECK_INTERVAL_SECONDS` | `5` | How often (seconds) the PDF pipeline polls for new PDF files. |
| `OCR_WORDS_PER_PAGE_THRESHOLD` | `50` | Pages with fewer than this many words are processed with OCR. |
| `OCR_LANGUAGE` | `eng` | Tesseract language code used for OCR. |
| `CHUNK_CHECK_INTERVAL_SECONDS` | `10` | How often (seconds) the chunking pipeline polls for pending work. |

---

## Logging

| Variable | Default | Description |
|---|---|---|
| `LOG_LEVEL` | `INFO` | Python logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |

---

## Internal / do not set externally

| Variable | Notes |
|---|---|
| `OLLAMA_API_BASE` | Set transiently by `providers.py` when calling a model via LiteLLM. If this variable is already present in the environment it will be temporarily overwritten and then restored. Do not set it externally. |

---

## Discrepancies

The following variables are accepted by the application but are **never set in any `docker-compose` file**; they always run on their defaults:

- `QDRANT_COLLECTION` (always `"library"`)
- `LANCEDB_PATH` (always `"/app/data/lancedb"`)
- `LANCEDB_TABLE` (always `"library"`)
- `PDF_CHECK_INTERVAL_SECONDS`, `OCR_WORDS_PER_PAGE_THRESHOLD`, `OCR_LANGUAGE`
- `CHUNK_CHECK_INTERVAL_SECONDS`
- `DEFAULT_SYSTEM_MESSAGE`

`CONVERSATION_WINDOW_LIMIT` is set to `2048` in `test_env_no_redis` and `test_env_self_hosted_llm` but is absent (unlimited) in all other environments including `test_env_default`.
