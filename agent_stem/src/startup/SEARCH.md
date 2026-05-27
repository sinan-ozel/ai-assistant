# Search

Vector search over the indexed document library, exposed as an HTTP endpoint
and a shared Python module used by both the endpoint and the DSL `retrieve()`
tool.

---

## Endpoint — `POST /private/v1/search`

Defined in `agent_stem/default/endpoints/private/search.py`.
Business logic lives in `agent_stem/src/common/search.py`.

### Request

```json
{
  "query":       "free-text search query",
  "collection":  "shelf1",
  "collections": ["shelf1", "shelf2"],
  "top_k":       5,
  "filter":      {"file_path": "shelf1/book.pdf"}
}
```

| Field         | Type            | Required | Description |
|---------------|-----------------|----------|-------------|
| `query`       | string          | one of `query`/`filter` required | Embedded and used for nearest-neighbour search. |
| `collection`  | string          | no       | Restrict to a single collection. Mutually exclusive with `collections`. |
| `collections` | array of strings| no       | Restrict to a set of collections. Mutually exclusive with `collection`. Omit to search all. |
| `top_k`       | integer         | no       | Maximum results to return. Default: `5`. |
| `filter`      | object          | one of `query`/`filter` required | Equality filters applied to payload fields. Keys are field names, values are the required values. |

Validation errors return HTTP 400:
- Neither `query` nor `filter` supplied.
- Both `collection` and `collections` supplied.

### Response

Results are streamed as **NDJSON** (`application/x-ndjson`). Each line is a
JSON object. The final line is the sentinel `{"done": true}`.

```jsonl
{"score": 0.48, "collection": "shelf1", "file_path": "shelf1/book.pdf", "text": "...", "section_title": "...", "book": {"title": "...", "tags": ["shelf1"]}, "chunking_completed_at": "..."}
{"done": true}
```

The response is also valid when read without streaming (`stream=False`): the
full body can be split on newlines and parsed line by line.

---

## Backend Selection

At query time, `run_search` probes Qdrant with a TCP connection:

- **Qdrant reachable** → uses `qdrant_client` for nearest-neighbour search
  or scroll (filter-only).
- **Qdrant unreachable** → uses LanceDB from `LANCEDB_PATH`.

The same routing applies when listing available collections/tables (used when
the caller does not specify any).

---

## Collection Routing

Mirrors the chunking pipeline: the top-level subfolder under `library/`
is the collection/table name. Files at the root of `library/` fall back to
`QDRANT_COLLECTION` / `LANCEDB_TABLE`.

---

## Score Normalisation

Both backends return scores in the same range so results can be compared
across environments:

| Backend  | Raw metric              | Formula                         | Effective metric          |
|----------|-------------------------|---------------------------------|---------------------------|
| Qdrant   | cosine similarity       | returned directly               | cosine similarity ∈ [-1, 1] |
| LanceDB  | L2 (squared Euclidean)  | `1 - distance / 2`              | cosine similarity ∈ [-1, 1] |

For unit-normalised embedding vectors the identity `cosine_sim = 1 - L2² / 2`
holds exactly, so both backends return the same score for the same query and
document.

---

## Filter-Only Search

When `query` is omitted but `filter` is provided, no embedding is computed:

- **Qdrant**: uses `client.scroll` with a `qdrant_client.http.models.Filter`.
- **LanceDB**: uses a SQL `WHERE` clause built from the filter dict (equality
  matches on string and numeric values only).

Filter-only results receive a score of `1.0`.

---

## Environment Variables

| Variable          | Default              | Description                              |
|-------------------|----------------------|------------------------------------------|
| `QDRANT_HOST`     | `qdrant`             | Qdrant hostname                          |
| `QDRANT_PORT`     | `6333`               | Qdrant port                              |
| `QDRANT_COLLECTION` | `library`          | Fallback collection name                 |
| `LANCEDB_PATH`    | `/app/data/lancedb`  | LanceDB data directory                   |
| `LANCEDB_TABLE`   | `library`            | Fallback table name                      |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | fastembed model name (runs in-process) |

---

## Test Coverage (`test_search.py`)

| Test | What it verifies |
|------|-----------------|
| `test_search_returns_results_as_expected` | Streaming search for `"psionic powers"`: validates NDJSON structure, `book` as dict with `tags` list, top result is `shelf1/simple-psionics.pdf`, score rounds to `0.48`. |
| `test_search_stream_false` | Same query without `stream=True`: verifies identical structure when the client buffers the full response. |
| `test_search_with_collection` | Search restricted to `collection="shelf1"` returns HTTP 200 with valid NDJSON. |
| `test_search_missing_query_and_filter_returns_400` | Omitting both `query` and `filter` returns HTTP 400. |
| `test_search_both_collection_and_collections_returns_400` | Supplying both `collection` and `collections` returns HTTP 400. |
| `test_search_with_filter` | Filter-only search by `file_path` returns HTTP 200 with valid NDJSON. |
