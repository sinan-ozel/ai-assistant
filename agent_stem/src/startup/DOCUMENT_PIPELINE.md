# Document Pipeline

Two background pipelines run at startup and process documents placed in the
`cortex/library` directory. They are chained: the PDF pipeline produces
Markdown files, and the chunking pipeline consumes them.

---

## Stage 1 — PDF Pipeline (`pdf_pipeline.py`)

Converts PDF files in `cortex/library` to Markdown (`.md`) files placed next
to the originals.

### Trigger

Runs on a polling loop every `PDF_CHECK_INTERVAL_SECONDS` (default: `5`).
Each PDF is re-processed when either:

- its SHA-256 hash differs from the stored value (file replaced or modified), or
- its `.md` sibling is missing (e.g. deleted manually).

Hidden files and files inside hidden folders (any path component starting with
`.`) are skipped.

### Process

1. **Hash check** — reads the file, computes SHA-256, compares to the value
   stored in Redis under `memory:pdf_pipeline_state`.
2. **Queue** — files that need conversion are marked `Queued` in Redis.
3. **Convert** — for each queued file, calls `pymupdf4llm.to_markdown`.
   - If the page word-count is below `OCR_WORDS_PER_PAGE_THRESHOLD` (default:
     `50` words/page), the PDF is assumed to be image-based and the conversion
     is retried with Tesseract OCR (`use_ocr=True`, language
     `OCR_LANGUAGE`, default: `eng`).
   - JPX image decode errors are handled with three fallback levels: retry
     with `ignore_images=True`, then page-by-page conversion skipping broken
     pages.
4. **Front matter** — a YAML block is prepended to the Markdown output
   containing: `filename`, `tags` (derived from the folder path relative to
   `library/`), `pdf_title`, `pdf_author`, `pages`, `ocr` (if OCR was used),
   and `body_title` (the single top-level Markdown header, when unique).
5. **Write** — the result is written to `<original_name>.md` beside the PDF.

### Redis State (`memory:pdf_pipeline_state`)

Each PDF is tracked by its absolute path:

| Status      | Meaning                                      |
|-------------|----------------------------------------------|
| `Checking`  | Hash is being compared right now             |
| `Queued`    | Change detected; awaiting conversion         |
| `Converting`| Conversion in progress                       |
| `Converted` | Up-to-date Markdown exists                   |

A missing entry means the file has never been seen.

### Environment Variables

| Variable                     | Default | Description                               |
|------------------------------|---------|-------------------------------------------|
| `PDF_CHECK_INTERVAL_SECONDS` | `5`     | Seconds between scan cycles               |
| `OCR_WORDS_PER_PAGE_THRESHOLD` | `50`  | Min words/page before OCR is triggered    |
| `OCR_LANGUAGE`               | `eng`   | Tesseract language code                   |

---

## Stage 2 — Chunking Pipeline (`chunking_pipeline.py`)

Reads Markdown files produced by Stage 1, splits them into semantic chunks,
embeds each chunk, and writes the results to the vector store.

### Trigger

Runs on a polling loop every `CHUNK_CHECK_INTERVAL_SECONDS` (default: `10`).
A Markdown file is re-processed when its `mtime` is newer than the
`chunking_completed_at` timestamp stored in Redis for that file.

Hidden files and files inside hidden folders are skipped.

### Process

1. **mtime check** — compares the file's modification time against
   `chunking_completed_at` stored in `memory:chunking_pipeline_state`.
2. **Parse** — reads the Markdown file and splits it into:
   - YAML front matter (via `MarkdownChunker.parse_frontmatter`)
   - Table of contents (stripped from the body via
     `MarkdownChunker.extract_toc_and_body`)
   - Body text
3. **Chunk** — `MarkdownChunker.chunk_markdown` performs a two-pass
   segmentation:
   - Pass 1: classifies each line (heading, TOC entry, body, page number,
     footer, etc.) and resolves page numbers from the TOC.
   - Pass 2: emits a new chunk at every ATX heading, carrying metadata:
     `section_title`, `section_title_in_toc`, `chapter_label_in_toc`,
     `page_number`, `token_count`, `parent_index`, `section_hierarchy`, and
     a `book` struct with the front-matter fields.
4. **Embed** — all chunk texts are sent as a single batch to the Ollama
   embedding server (`POST /api/embed`). The embedding dimension is resolved
   once and cached.
5. **Write** — chunks and vectors are written to the vector store:
   - **Qdrant** (preferred) — if reachable at `QDRANT_HOST:QDRANT_PORT`.
     Each chunk is a point with a deterministic UUID and a flat payload.
     `page_number` and `parent_index` use `-1` for null.
   - **LanceDB** (fallback) — if Qdrant is unreachable. The table is created
     with an explicit PyArrow schema so that `book` is stored as a
     native struct and `section_hierarchy` as a native list, not as JSON
     strings. `page_number` and `parent_index` use `-1` for null.
6. **State update** — `chunking_completed_at` is written to Redis
     (`memory:chunking_pipeline_state`) using the timestamp from step 5
     so that it exactly matches the value stored in each chunk's payload.

### Collection Routing

The top-level subfolder under `library/` becomes the collection/table name.
Files placed directly under `library/` (no subfolder) fall back to
`QDRANT_COLLECTION` / `LANCEDB_TABLE`.

Example: `library/shelf1/book.md` → collection `shelf1`.

### Redis State (`memory:chunking_pipeline_state`)

Each Markdown file is tracked by its absolute path:

| Status     | Meaning                                         |
|------------|-------------------------------------------------|
| `Checking` | mtime is being compared right now               |
| `Queued`   | File is newer than last `chunking_completed_at` |
| `Chunking` | Chunking/embedding/writing in progress          |
| `Chunked`  | Up-to-date chunks exist in the vector store     |

A missing entry means the file has never been processed.

### Environment Variables

| Variable                      | Default              | Description                             |
|-------------------------------|----------------------|-----------------------------------------|
| `CHUNK_CHECK_INTERVAL_SECONDS`| `10`                 | Seconds between scan cycles             |
| `QDRANT_HOST`                 | `qdrant`             | Qdrant hostname                         |
| `QDRANT_PORT`                 | `6333`               | Qdrant port                             |
| `QDRANT_COLLECTION`           | `library`            | Fallback collection name                |
| `LANCEDB_PATH`                | `/app/data/lancedb`  | LanceDB data directory                  |
| `LANCEDB_TABLE`               | `library`            | Fallback table name                     |
| `EMBEDDING_MODEL`             | `nomic-ai/nomic-embed-text-v1.5` | fastembed model name (runs in-process) |

---

## Data Flow

```
cortex/library/
  shelf1/
    book.pdf   ──[PDF pipeline]──▶  book.md  ──[Chunking pipeline]──▶  Qdrant / LanceDB
```

Both pipelines run concurrently. The chunking pipeline discovers the Markdown
file on its next poll after the PDF pipeline writes it.

---

## Test Coverage (`test_pipeline.py`)

| Test | What it verifies |
|------|-----------------|
| `test_pdf_converted_to_markdown` | Every visible PDF produces a non-empty `.md` sibling; spot-checks content of `shelf1/simple-psionics.md`. |
| `test_chunks_stored_in_qdrant` | End-to-end: after state reset, polls `POST /private/v1/search` until at least one result is returned (stream=True). |
| `test_qdrant_updates_after_frontmatter_edit` | Editing the YAML front matter of a Markdown file triggers a re-chunk; the `chunking_completed_at` timestamp in search results advances. |
| `test_books_endpoint` | `GET /private/v1/books` lists every visible PDF with correct `tags` and `chunk_count > 0`. |

The fixtures `pdf_conversion_reset` and `chunk_reset` clear the relevant
Redis keys (and Qdrant collections when reachable) before each test so the
pipelines start from a clean state.
