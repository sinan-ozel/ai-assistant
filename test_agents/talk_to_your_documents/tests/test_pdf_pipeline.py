"""Tests for the PDF-to-Markdown conversion pipeline."""

import time

import pytest

# Allow enough time for one check cycle (PDF_CHECK_INTERVAL_SECONDS=5)
# plus the actual pymupdf4llm conversion.
TIMEOUT = 180  # seconds


@pytest.mark.depends(on=["healthy"])
def test_pdf_converted_to_markdown(pdf_conversion_reset):
    """Pipeline should create a .md file next to every PDF in the library.

    The fixture clears Redis state and deletes all .md files so the
    pipeline treats every PDF as new. The test polls until all expected
    Markdown files have reappeared, including those in subdirectories.
    """
    md_paths = pdf_conversion_reset
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
