# Document Library (RAG)

Drop documents into `cortex/library/` and they are automatically processed into a vector store.
Your agent can then retrieve relevant chunks at query time — either directly in `prompt.py`
via `Search()`, or by giving the LLM an MCP tool it can call autonomously.

## How it works

Two background pipelines run at startup:

```
cortex/library/
  shelf1/
    my-book.pdf   ──[PDF pipeline]──▶  my-book.md  ──[Chunking pipeline]──▶  Qdrant / LanceDB
```

1. **PDF pipeline** — converts PDFs to Markdown. Detects image-based PDFs and applies OCR automatically.
2. **Chunking pipeline** — reads Markdown, splits by headings, embeds chunks, writes to the vector store.

Both pipelines poll for changes on a configurable interval. Add or replace a file and it will be
re-processed automatically on the next cycle.

## Organising documents into collections

The top-level subfolder becomes the collection name in the vector store:

```
library/
  shelf1/       ← collection: "shelf1"
    book-a.pdf
    book-b.pdf
  shelf2/       ← collection: "shelf2"
    book-c.pdf
  flat-doc.pdf  ← falls back to QDRANT_COLLECTION (default: "library")
```

Collections let you scope searches to a subset of your library.

## Supported formats

| Format | Notes |
|---|---|
| `.pdf` | Converted to Markdown by the PDF pipeline. OCR applied if the page word count is below threshold. |
| `.md` | Processed directly by the chunking pipeline (skips the PDF stage). |

## Vector stores

The chunking pipeline writes to **Qdrant** by default. If Qdrant is unreachable, it falls back
to **LanceDB** automatically.

| Store | When used |
|---|---|
| Qdrant | Default. Requires `qdrant` service in docker-compose. |
| LanceDB | Fallback. No extra service needed; data stored under `LANCEDB_PATH`. |

---

## Approach 1 — Direct retrieval with `Search()` (LanceDB or Qdrant)

`Search()` runs a vector search from inside `prompt.py` on every request. The retrieved
chunks are injected into the prompt before the user message is sent to the LLM.
This approach works with both Qdrant and LanceDB.

```python
# cortex/chat/prompt.py

"""
You are an assistant with access to a library of documents.
Use the retrieved context to answer questions accurately.
"""

results = Search(input_text)

if results:
    print("Relevant context:")
    print(results)

print(input_text)
```

Search returns a formatted string of the most relevant chunks. By default it returns
the top 5 results (`top_k=5`).

### Restrict to a single collection

```python
results = Search(input_text, "shelf1")
```

### Full example with multiple collections

```python
"""
You are a city guide assistant with access to information about Oldtown and Newtown.
Answer questions using only the facts from the relevant collection.
"""

results = Search(input_text, "oldtown")

if results:
    print("Context from the Oldtown guide:")
    print(results)

print(input_text)
```

---

## Approach 2 — MCP tool search (Qdrant required)

`McpServer()` gives the LLM a `library_search` tool it can call autonomously. Instead of
always retrieving context up front, the LLM decides when to search and what to ask.
**This approach requires Qdrant** — the MCP tool calls `run_search` which talks directly
to Qdrant. LanceDB is not used as a fallback here.

```python
# cortex/chat/prompt.py

"""
You are a knowledgeable guide. Use the available tools to answer questions accurately.
"""

with McpServer():
    prompt()

response = prompt()
```

`McpServer()` with no arguments connects to the built-in MCP server running on port 8001
inside the same container. The `library_search` tool is registered automatically from
`agent_stem/default/mcp/tools/search.py`.

### What the LLM receives

The LLM sees a tool called `library_search` with these parameters:

| Parameter | Type | Description |
|---|---|---|
| `query` | string | Natural-language search query |
| `collection` | string | Qdrant collection to search (empty = all collections) |
| `top_k` | integer | Maximum number of chunks to return (default: 5) |
| `book` | object | Filter by book metadata (see below) |

### Filtering by book metadata

The `book` parameter narrows results by any of the fields the ingestion pipelines
attach to each chunk. Pass a flat dict — keys with an empty string are ignored:

| Key | Matches |
|---|---|
| `tags` | Top-level library subfolder (collection label), e.g. `"shelf2"` |
| `title_from_pdf` | Exact PDF document title |
| `author_from_pdf` | Exact PDF document author |

Example the LLM might produce (or you can set defaults in your prompt):

```json
{ "query": "psionic powers", "book": { "tags": "shelf1" } }
```

### Rich results

Each result includes full provenance extracted during ingestion:

```
[1] score=0.831
  source:    shelf1/simple-psionics.pdf
  book:      Simple Psionics
  author:    Jane Doe
  tags:      shelf1
  chapter:   Chapter 3
  path:      Introduction > Core Rules
  section:   Psionic Disciplines
  page:      42

Psionic disciplines define the scope of a character's mental abilities ...
```

### When Qdrant is unavailable

If Qdrant is unreachable when `library_search` is called, the tool returns a brief
message to the LLM (`"Library search is unavailable."`) and logs a detailed diagnostic
to the container log including the hostname, port, current environment variable values,
and step-by-step instructions for fixing the connection.

### Qdrant setup

Add the Qdrant service to your `docker-compose.yml`:

```yaml
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
```

Set `QDRANT_HOST` and `QDRANT_PORT` in the app service environment if they differ
from the defaults (`qdrant` and `6333`).

---

## Choosing between the two approaches

| | `Search()` | `McpServer()` + `library_search` |
|---|---|---|
| Qdrant required | No (falls back to LanceDB) | Yes |
| When retrieval runs | Every request, unconditionally | LLM decides when to call the tool |
| Best for | Known retrieval pattern; always need context | Open-ended queries; LLM should judge when to search |
| Multi-turn | Same retrieval on every turn | LLM can search multiple times or skip entirely |

You can use both in the same `prompt.py`:

```python
"""You are a research assistant."""

# Always retrieve basic context up front
results = Search(input_text)
if results:
    print(results)

# Also give the LLM a tool for follow-up searches
with McpServer():
    prompt()

response = prompt()
```

---

## Hidden files and folders

Files and folders whose names start with `.` are skipped by both pipelines:

```
library/
  .eberron/       ← hidden — not processed
  shelf1/
    .draft.pdf    ← hidden — not processed
    final.pdf     ← processed normally
```

## Monitoring pipeline status

Use the private books endpoint to check ingestion status:

```bash
curl http://localhost:8000/private/v1/books
```

Returns a list of all visible PDFs with their `tags` (collection) and `chunk_count`.
A `chunk_count > 0` means the document has been successfully ingested.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `EMBEDDING_SERVER` | `http://embedding:11434` | Ollama base URL for the embedding model |
| `EMBEDDING_MODEL` | `all-minilm:33m` | Embedding model name |
| `QDRANT_HOST` | `qdrant` | Qdrant hostname |
| `QDRANT_PORT` | `6333` | Qdrant port |
| `QDRANT_COLLECTION` | `library` | Fallback collection for files at the library root |
| `LANCEDB_PATH` | `/app/data/lancedb` | LanceDB data directory |
| `PDF_CHECK_INTERVAL_SECONDS` | `5` | How often to scan for new/changed PDFs |
| `CHUNK_CHECK_INTERVAL_SECONDS` | `10` | How often to scan for new/changed Markdown files |
| `OCR_WORDS_PER_PAGE_THRESHOLD` | `50` | Min words/page before OCR is triggered |
| `OCR_LANGUAGE` | `eng` | Tesseract language code |
