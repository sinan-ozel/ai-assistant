"""Tests for the PDF → Markdown → Qdrant pipeline."""

import time
from pathlib import Path

import pytest

LIBRARY_DIR = Path("/app/cortex/library")

# Allow enough time for one check cycle (PDF_CHECK_INTERVAL_SECONDS=5)
# plus the actual pymupdf4llm conversion.
TIMEOUT = 180  # seconds

# Allow time for PDF conversion + embedding model + chunking to complete.
CHUNK_TIMEOUT = 600  # seconds

QDRANT_COLLECTION = "library"


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
            info = qdrant.get_collection(QDRANT_COLLECTION)
            if info.points_count and info.points_count > 0:
                break
        except Exception:
            pass  # collection not yet created

        if time.time() - start > CHUNK_TIMEOUT:
            raise TimeoutError(
                f"No points in Qdrant collection '{QDRANT_COLLECTION}' "
                f"after {CHUNK_TIMEOUT} seconds."
            )
        time.sleep(5)

    # TODO: add more specific checks — e.g. verify metadata fields,
    # spot-check a known chunk from simple-psionics, run a semantic search.
