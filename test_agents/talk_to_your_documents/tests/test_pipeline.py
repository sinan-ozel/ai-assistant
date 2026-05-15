"""Tests for the PDF → Markdown → Qdrant pipeline."""

import json
import os
import time
from pathlib import Path

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

LIBRARY_DIR = Path("/app/cortex/library")

# Allow enough time for one check cycle (PDF_CHECK_INTERVAL_SECONDS=5)
# plus the actual pymupdf4llm conversion.
TIMEOUT = 180  # seconds

# Allow time for PDF conversion + embedding model + chunking to complete.
CHUNK_TIMEOUT = 1200  # seconds


@pytest.mark.depends(on=["healthy"])
def test_pdf_converted_to_markdown(pdf_conversion_reset):
    """Pipeline should create a .md file next to every visible PDF in the library.

    The fixture clears Redis state and deletes existing .md files so the
    pipeline treats every PDF as new. The test derives the expected Markdown
    paths itself and polls until they have all reappeared.
    """
    md_paths = [
        p.with_suffix(".md")
        for p in LIBRARY_DIR.rglob("*.pdf")
        if not any(part.startswith(".") for part in p.parts[len(LIBRARY_DIR.parts) :])
    ]
    assert md_paths, "No PDFs found in the library — nothing to test."

    pending = set(md_paths)
    start = time.time()
    while pending:
        pending = {p for p in pending if not p.exists()}
        if not pending:
            break
        if time.time() - start > TIMEOUT:
            names = ", ".join(p.name for p in sorted(pending))
            raise TimeoutError(
                f"These files did not appear within {TIMEOUT} seconds: {names}"
            )
        time.sleep(1)

    for md_path in md_paths:
        assert md_path.stat().st_size > 0, f"{md_path.name} exists but is empty."

    shelf1_md = next(
        (p for p in md_paths if "shelf1" in p.parts and p.name == "simple-psionics.md"),
        None,
    )
    assert shelf1_md is not None, "shelf1/simple-psionics.md not found among converted files."

    content = shelf1_md.read_text(encoding="utf-8")
    assert "_Carrie_" in content, "_Carrie_ not found in shelf1/simple-psionics.md."

    for line in content.splitlines():
        if "_Carrie_" in line:
            break
    else:
        pytest.fail("_Carrie_ not found in any line of shelf1/simple-psionics.md.")


@pytest.mark.depends(on=["healthy"])
def test_chunks_stored_in_qdrant(pdf_conversion_reset, chunk_reset):
    """End-to-end: PDFs should be converted, chunked, and searchable.

    Both pipelines run continuously in the background. Resetting their Redis
    state and dropping the Qdrant collection forces a full reprocess. The test
    polls the search endpoint until at least one result is returned.
    """
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
            results = [p for p in parsed if not p.get("done")]
            if results:
                break

        if time.time() - start > CHUNK_TIMEOUT:
            raise TimeoutError(
                f"No search results returned within {CHUNK_TIMEOUT} seconds."
            )
        time.sleep(5)


@pytest.mark.depends(on=["test_chunks_stored_in_qdrant"])
def test_qdrant_updates_after_frontmatter_edit(pdf_conversion_reset, chunk_reset):
    """Editing a Markdown frontmatter should trigger a re-chunk visible via search.

    Steps:
    1. Wait for shelf1/simple-psionics.md to be converted from its PDF.
    2. Wait for its chunks to be searchable; record chunking_completed_at.
    3. Add a field to the frontmatter YAML (touches mtime → triggers re-chunk).
    4. Wait for the search endpoint to return a newer chunking_completed_at.
    """
    md_path = LIBRARY_DIR / "shelf1" / "simple-psionics.md"

    # Step 1: wait for the markdown file to appear
    start = time.time()
    while not md_path.exists():
        if time.time() - start > TIMEOUT:
            raise TimeoutError(
                f"{md_path} is missing — the PDF pipeline did not create it within {TIMEOUT}s"
            )
        time.sleep(1)

    # Step 2: wait for chunks to be searchable; record the timestamp
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

    # Step 3: add a field to the frontmatter — this touches mtime
    content = md_path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        pytest.fail(
            f"{md_path} exists but is missing the YAML front matter '---' delimiter"
        )
    _, fm, body = parts
    md_path.write_text(f"---{fm}test_note: added_by_test\n---{body}", encoding="utf-8")

    # Step 4: wait for the search endpoint to reflect a newer chunking_completed_at
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
                new_completed_at = results[0].get("chunking_completed_at")
                if new_completed_at and new_completed_at != original_completed_at:
                    break
        if time.time() - start > CHUNK_TIMEOUT:
            raise TimeoutError(
                f"Search results not updated after frontmatter edit within {CHUNK_TIMEOUT}s"
            )
        time.sleep(5)


@pytest.mark.depends(on=["test_chunks_stored_in_qdrant"], name="test_books_endpoint")
def test_books_endpoint(pdf_conversion_reset, chunk_reset):
    """GET /private/v1/books should list every book processed by the pipeline.

    Waits for at least one book to appear in the endpoint, then checks that
    every visible PDF in the library has a corresponding entry with the correct
    fields.
    """
    expected_paths = {
        str(p.relative_to(LIBRARY_DIR).with_suffix(".pdf"))
        for p in LIBRARY_DIR.rglob("*.pdf")
        if not any(part.startswith(".") for part in p.parts[len(LIBRARY_DIR.parts) :])
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
            missing = expected_paths - found
            raise TimeoutError(
                f"/private/v1/books missing entries after {CHUNK_TIMEOUT}s: {missing}"
            )
        time.sleep(5)

    by_path = {b["file_path"]: b for b in books}
    for path in expected_paths:
        assert path in by_path, f"{path} not found in /private/v1/books"
        book = by_path[path]
        assert isinstance(book["tags"], list), f"{path}: 'tags' must be a list"
        assert isinstance(book["chunk_count"], int), f"{path}: 'chunk_count' must be an int"
        assert book["chunk_count"] > 0, f"{path}: 'chunk_count' must be > 0"
