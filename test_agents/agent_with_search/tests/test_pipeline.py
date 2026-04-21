"""Tests that the PDF pipeline ingests library documents.

Verifies that every PDF in the agent's library is processed end-to-end:
converted to Markdown, chunked, embedded, and stored in the vector store.
"""

import os
import time

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")

# Allow enough time for PDF conversion + embedding + chunking to complete.
CHUNK_TIMEOUT = 900  # seconds

EXPECTED_BOOKS = {
    "shelf2/lycanthropes-in-eberron.pdf",
}


@pytest.mark.depends(on=["healthy"], name="test_books_ingested")
def test_books_ingested():
    """All library PDFs should be converted, chunked, and listed by /private/v1/books.

    The fixture clears the chunking pipeline state and drops Qdrant
    collections so the pipeline starts from scratch. The test then polls
    until every expected book appears with chunk_count > 0.
    """
    start = time.time()
    while True:
        resp = requests.get(f"{BASE_URL}/private/v1/books")
        assert resp.status_code == 200, (
            f"Unexpected status from /private/v1/books: {resp.status_code}"
        )
        books = resp.json()
        by_path = {b["file_path"]: b for b in books}

        if all(
            path in by_path and by_path[path]["chunk_count"] > 0
            for path in EXPECTED_BOOKS
        ):
            break

        if time.time() - start > CHUNK_TIMEOUT:
            found = {b["file_path"] for b in books}
            missing = EXPECTED_BOOKS - found
            not_chunked = {
                path
                for path in EXPECTED_BOOKS & found
                if by_path.get(path, {}).get("chunk_count", 0) == 0
            }
            raise TimeoutError(
                f"Books not fully ingested after {CHUNK_TIMEOUT}s. "
                f"Missing: {missing}, not chunked: {not_chunked}"
            )
        time.sleep(5)

    for path in EXPECTED_BOOKS:
        book = by_path[path]
        assert isinstance(book["tags"], list), (
            f"{path}: 'tags' must be a list"
        )
        assert isinstance(book["chunk_count"], int), (
            f"{path}: 'chunk_count' must be an int"
        )
        assert book["chunk_count"] > 0, (
            f"{path}: 'chunk_count' must be > 0"
        )
