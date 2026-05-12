"""Tests that the PDF pipeline ingests library documents."""

import os
import time

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")

CHUNK_TIMEOUT = 900  # seconds

EXPECTED_BOOKS = {
    "shelf1/lycanthropes-in-eberron.pdf",
}


@pytest.mark.depends(on=["healthy"], name="test_books_ingested")
def test_books_ingested(chunk_reset):
    """All library PDFs should be converted, chunked, and listed by /private/v1/books."""
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
        assert isinstance(book["tags"], list)
        assert isinstance(book["chunk_count"], int)
        assert book["chunk_count"] > 0
