"""Library books endpoint."""

import os
import time

from fastapi import HTTPException

QDRANT_HOST = os.environ.get("QDRANT_HOST")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
LANCEDB_PATH = os.environ.get("LANCEDB_PATH", "/app/data/lancedb")
_QDRANT_TIMEOUT = 1.0


def _books_from_qdrant() -> list[dict]:
    from qdrant_client import QdrantClient

    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=_QDRANT_TIMEOUT)
    books: dict[str, dict] = {}
    for collection in client.get_collections().collections:
        offset = None
        while True:
            results, next_offset = client.scroll(
                collection_name=collection.name,
                limit=256,
                offset=offset,
                with_payload=["file_path", "book"],
                with_vectors=False,
            )
            for point in results:
                fp = point.payload.get("file_path")
                if not fp:
                    continue
                if fp not in books:
                    book = point.payload.get("book") or {}
                    tags = book.get("tags", []) if isinstance(book, dict) else []
                    books[fp] = {"tags": tags, "chunk_count": 0}
                books[fp]["chunk_count"] += 1
            if next_offset is None:
                break
            offset = next_offset
    result = [{"file_path": fp, **info} for fp, info in books.items()]
    for entry in result:
        for key, val in entry.items():
            if not isinstance(val, (str, int, float, bool, list, dict, type(None))):
                raise TypeError(
                    f"Qdrant returned non-serializable type {type(val).__name__!r} "
                    f"for field {key!r}: {val!r}"
                )
    return result


def _books_from_lancedb() -> list[dict]:
    import lancedb

    db = lancedb.connect(LANCEDB_PATH)
    books: dict[str, dict] = {}
    for table_name in db.table_names():
        tbl = db.open_table(table_name)
        df = tbl.to_pandas()
        for _, row in df.iterrows():
            fp = row.get("file_path")
            if not fp:
                continue
            book = row.get("book") or {}
            tags = list(book.get("tags") or []) if isinstance(book, dict) else []
            if fp not in books:
                books[fp] = {"tags": tags, "chunk_count": 0}
            books[fp]["chunk_count"] += 1
    result = [{"file_path": fp, **info} for fp, info in books.items()]
    for entry in result:
        for key, val in entry.items():
            if not isinstance(val, (str, int, float, bool, list, dict, type(None))):
                raise TypeError(
                    f"LanceDB returned non-serializable type {type(val).__name__!r} "
                    f"for field {key!r}: {val!r}"
                )
    return result


async def handler():
    """Return the list of books indexed by the chunking pipeline."""
    if QDRANT_HOST:
        start = time.time()
        try:
            return _books_from_qdrant()
        except Exception as e:
            elapsed = time.time() - start
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Cannot reach Qdrant — QDRANT_HOST is set to "
                    f"'{QDRANT_HOST}:{QDRANT_PORT}' but the server did not respond "
                    f"(elapsed: {elapsed:.2f}s, error: {e}). "
                    f"Check that QDRANT_HOST points to the correct host."
                ),
            )
    return _books_from_lancedb()


spec = {
    "path": "/private/v1/books",
    "methods": ["GET"],
    "summary": "List indexed books",
    "description": (
        "Return all books that have been processed by the chunking pipeline. "
        "Each entry includes the book's file path relative to the library root "
        "(with a .pdf extension), its tags, and the number of chunks stored in "
        "the vector store."
    ),
    "responses": {
        200: {
            "description": "List of indexed books",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": (
                                        "Path to the source PDF relative to the "
                                        "library root, e.g. 'shelf1/my-book.pdf'"
                                    ),
                                },
                                "tags": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": (
                                        "Tags inherited from the book's YAML "
                                        "front matter"
                                    ),
                                },
                                "chunk_count": {
                                    "type": "integer",
                                    "description": (
                                        "Number of chunks stored in the vector "
                                        "store for this book"
                                    ),
                                },
                            },
                            "required": ["file_path", "tags", "chunk_count"],
                        },
                    },
                    "example": [
                        {
                            "file_path": "shelf1/simple-psionics.pdf",
                            "tags": ["shelf1"],
                            "chunk_count": 51,
                        },
                        {
                            "file_path": "shelf2/FashionDesigner.pdf",
                            "tags": ["shelf2"],
                            "chunk_count": 5,
                        },
                    ],
                }
            },
        }
    },
}
