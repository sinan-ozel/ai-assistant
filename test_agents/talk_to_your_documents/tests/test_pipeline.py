"""Tests for the PDF → Markdown → vector-store pipeline."""

import json
import os
import time
from pathlib import Path

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

LIBRARY_DIR = Path("/app/cortex/library")

# Allow enough time for one PDF conversion cycle, including any pipeline
# re-runs triggered by file detection ordering during session setup.
TIMEOUT = 360  # seconds

# Allow time for PDF conversion + embedding model + chunking to complete.
CHUNK_TIMEOUT = 1200  # seconds

_PDF_PARAMS = [
    pytest.param("shelf1/simple-psionics.pdf", "_Carrie_", id="simple-psionics"),
    pytest.param("shelf2/FashionDesigner.pdf", None, id="FashionDesigner"),
    pytest.param("shelf2/lycanthropes-in-eberron.pdf", None, id="lycanthropes"),
]


@pytest.mark.depends(on=["healthy"])
@pytest.mark.parametrize("rel_path,check_content", _PDF_PARAMS)
def test_pdf_converted_to_markdown(rel_path, check_content):
    """Pipeline creates a .md file next to each PDF placed in the library."""
    expected_md = (LIBRARY_DIR / rel_path).with_suffix(".md")
    start = time.time()
    while not expected_md.exists():
        if time.time() - start > TIMEOUT:
            raise TimeoutError(
                f"{expected_md.name} did not appear within {TIMEOUT}s"
            )
        time.sleep(1)
    assert expected_md.stat().st_size > 0, f"{expected_md.name} is empty"
    if check_content:
        content = expected_md.read_text(encoding="utf-8")
        assert check_content in content, (
            f"{check_content!r} not found in {expected_md.name}"
        )


@pytest.mark.depends(on=[
    "test_pdf_converted_to_markdown[simple-psionics]",
    "test_pdf_converted_to_markdown[FashionDesigner]",
    "test_pdf_converted_to_markdown[lycanthropes]",
])
def test_chunks_stored_in_qdrant():
    """All PDFs should be chunked and searchable before search tests run."""
    start = time.time()
    while True:
        resp = requests.post(
            f"{BASE_URL}/private/v1/search",
            json={"query": "psionic", "top_k": 1},
            stream=True,
        )
        if resp.status_code == 200:
            lines = [line for line in resp.iter_lines() if line]
            parsed = [json.loads(line) for line in lines]
            if any(not p.get("done") for p in parsed):
                break
        if time.time() - start > CHUNK_TIMEOUT:
            raise TimeoutError(
                f"No search results returned within {CHUNK_TIMEOUT}s"
            )
        time.sleep(5)


@pytest.mark.depends(on=["test_chunks_stored_in_qdrant"])
def test_qdrant_updates_after_frontmatter_edit():
    """Editing a Markdown frontmatter triggers a re-chunk visible via search."""
    md_path = LIBRARY_DIR / "shelf1" / "simple-psionics.md"
    assert md_path.exists(), f"{md_path} missing — prior test should have ensured it"

    # Record the current chunking_completed_at before the edit.
    original_completed_at = None
    start = time.time()
    while original_completed_at is None:
        resp = requests.post(
            f"{BASE_URL}/private/v1/search",
            json={"filter": {"file_path": "shelf1/simple-psionics.pdf"}, "top_k": 1},
            stream=True,
        )
        if resp.status_code == 200:
            lines = [line for line in resp.iter_lines() if line]
            parsed = [json.loads(line) for line in lines]
            results = [p for p in parsed if not p.get("done")]
            if results:
                original_completed_at = results[0].get("chunking_completed_at")
        if original_completed_at is None:
            if time.time() - start > CHUNK_TIMEOUT:
                raise TimeoutError(
                    f"No search results for simple-psionics.pdf after {CHUNK_TIMEOUT}s"
                )
            time.sleep(5)

    # Touch the frontmatter to trigger a re-chunk.
    content = md_path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        pytest.fail(f"{md_path} is missing YAML front matter '---' delimiter")
    _, fm, body = parts
    md_path.write_text(f"---{fm}test_note: added_by_test\n---{body}", encoding="utf-8")

    # Wait for the search endpoint to reflect a newer chunking_completed_at.
    start = time.time()
    while True:
        resp = requests.post(
            f"{BASE_URL}/private/v1/search",
            json={"filter": {"file_path": "shelf1/simple-psionics.pdf"}, "top_k": 1},
            stream=True,
        )
        if resp.status_code == 200:
            lines = [line for line in resp.iter_lines() if line]
            parsed = [json.loads(line) for line in lines]
            results = [p for p in parsed if not p.get("done")]
            if results:
                new_ts = results[0].get("chunking_completed_at")
                if new_ts and new_ts != original_completed_at:
                    break
        if time.time() - start > CHUNK_TIMEOUT:
            raise TimeoutError(
                f"Search not updated after frontmatter edit within {CHUNK_TIMEOUT}s"
            )
        time.sleep(5)


@pytest.mark.depends(on=["test_chunks_stored_in_qdrant"], name="test_books_endpoint")
def test_books_endpoint():
    """GET /private/v1/books should list every PDF processed by the pipeline."""
    expected_paths = {
        str(p.relative_to(LIBRARY_DIR).with_suffix(".pdf"))
        for p in LIBRARY_DIR.rglob("*.pdf")
        if not any(part.startswith(".") for part in p.parts[len(LIBRARY_DIR.parts):])
    }
    assert expected_paths, "No PDFs found in the library — nothing to test."

    start = time.time()
    while True:
        resp = requests.get(f"{BASE_URL}/private/v1/books")
        assert resp.status_code == 200, f"Unexpected status: {resp.status_code}"
        books = resp.json()
        if len(books) >= len(expected_paths):
            break
        if time.time() - start > CHUNK_TIMEOUT:
            found = {b["file_path"] for b in books}
            raise TimeoutError(
                f"/private/v1/books missing entries after {CHUNK_TIMEOUT}s: "
                f"{expected_paths - found}"
            )
        time.sleep(5)

    by_path = {b["file_path"]: b for b in books}
    for path in expected_paths:
        assert path in by_path, f"{path} not in /private/v1/books"
        book = by_path[path]
        assert isinstance(book["tags"], list), f"{path}: 'tags' must be a list"
        assert isinstance(book["chunk_count"], int), f"{path}: 'chunk_count' must be int"
        assert book["chunk_count"] > 0, f"{path}: 'chunk_count' must be > 0"
