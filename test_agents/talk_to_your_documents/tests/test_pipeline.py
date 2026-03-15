"""Tests for the PDF → Markdown → Qdrant pipeline."""

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
CHUNK_TIMEOUT = 600  # seconds

QDRANT_FALLBACK_COLLECTION = "library"


def _collection_for_path(md_path: Path) -> str:
    """Mirror the pipeline's logic: top-level folder under LIBRARY_DIR is the collection."""
    parts = md_path.relative_to(LIBRARY_DIR).parts
    return parts[0] if len(parts) > 1 else QDRANT_FALLBACK_COLLECTION


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
        if not any(part.startswith(".") for part in p.parts[len(LIBRARY_DIR.parts):])
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
    """End-to-end: PDFs should be converted, chunked, and appear in Qdrant.

    Both pipelines run continuously in the background. Resetting their Redis
    state and dropping the Qdrant collection forces a full reprocess. The test
    polls until at least one point shows up in the collection.
    """
    qdrant = chunk_reset

    start = time.time()
    while True:
        try:
            total = sum(
                qdrant.get_collection(c.name).points_count or 0
                for c in qdrant.get_collections().collections
            )
            if total > 0:
                break
        except Exception:
            pass  # collections not yet created

        if time.time() - start > CHUNK_TIMEOUT:
            raise TimeoutError(
                f"No points in Qdrant collection '{QDRANT_COLLECTION}' "
                f"after {CHUNK_TIMEOUT} seconds."
            )
        time.sleep(5)

    # TODO: add more specific checks — e.g. verify metadata fields,
    # spot-check a known chunk from simple-psionics, run a semantic search.


@pytest.mark.depends(on=["test_chunks_stored_in_qdrant"])
def test_qdrant_updates_after_frontmatter_edit(pdf_conversion_reset, chunk_reset):
    """Editing a Markdown frontmatter should trigger a re-chunk in Qdrant.

    Steps:
    1. Wait for shelf1/simple-psionics.md to be converted from its PDF.
    2. Wait for its chunks to appear in Qdrant; record chunking_completed_at.
    3. Add a field to the frontmatter YAML (touches mtime → triggers re-chunk).
    4. Wait for Qdrant to show a newer chunking_completed_at for that file.
    """
    from qdrant_client.http import models as qmodels

    qdrant = chunk_reset
    md_path = LIBRARY_DIR / "shelf1" / "simple-psionics.md"
    collection = _collection_for_path(md_path)
    file_path = str(md_path.relative_to(LIBRARY_DIR).with_suffix(".pdf"))
    point_filter = qmodels.Filter(
        must=[
            qmodels.FieldCondition(
                key="file_path",
                match=qmodels.MatchValue(value=file_path),
            )
        ]
    )

    # Step 1: wait for the markdown file to appear
    start = time.time()
    while not md_path.exists():
        if time.time() - start > TIMEOUT:
            raise TimeoutError(
                f"{md_path} is missing — the PDF pipeline did not create it within {TIMEOUT}s"
            )
        time.sleep(1)

    # Step 2: wait for its chunks to land in Qdrant; record the timestamp
    original_completed_at = None
    start = time.time()
    while original_completed_at is None:
        try:
            results, _ = qdrant.scroll(
                collection_name=collection,
                scroll_filter=point_filter,
                limit=1,
                with_payload=True,
            )
            if results:
                original_completed_at = results[0].payload.get("chunking_completed_at")
        except Exception:
            pass
        if original_completed_at is None:
            if time.time() - start > CHUNK_TIMEOUT:
                raise TimeoutError(
                    f"No Qdrant points for {md_path.name} after {CHUNK_TIMEOUT}s"
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

    # Step 4: wait for Qdrant to show a newer chunking_completed_at
    start = time.time()
    while True:
        try:
            results, _ = qdrant.scroll(
                collection_name=collection,
                scroll_filter=point_filter,
                limit=1,
                with_payload=True,
            )
            if results:
                new_completed_at = results[0].payload.get("chunking_completed_at")
                if new_completed_at and new_completed_at != original_completed_at:
                    break
        except Exception:
            pass
        if time.time() - start > CHUNK_TIMEOUT:
            raise TimeoutError(
                f"Qdrant was not updated after frontmatter edit within {CHUNK_TIMEOUT}s"
            )
        time.sleep(5)

    # TODO: verify results[0].payload["book"] contains test_note: added_by_test
