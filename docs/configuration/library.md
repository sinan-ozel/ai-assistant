# Document Library (RAG)

Drop documents into `cortex/library/` and they are automatically processed into a vector store.
Your agent can then retrieve relevant chunks at query time.

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

Collections let you scope searches to a subset of your library. Search a specific collection
from `prompt.py`:

```python
results = Search(input_text, "shelf1")
```

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

## Hidden files and folders

Files and folders whose names start with `.` are skipped by both pipelines. Use this to keep
files in the library directory without indexing them:

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

## Search from `prompt.py`

```python
"""
You are an assistant with access to a library of documents.
Use the retrieved context to answer questions.
"""

results = Search(input_text)

if results:
    print("Relevant context:")
    print(results)

print(input_text)
```

Search returns a formatted string of the most relevant chunks. By default it returns
the top 5 results (`top_k=5`).

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
