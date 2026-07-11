"""Tests for library reconciliation: deleted files must leave the index.

Scenarios covered, in dependency order:

1. Baseline — every fixture (PDFs and a hand-authored .md) is ingested.
2. Deleting a PDF cascades: generated .md removed, book gone from the index.
3. The hand-authored .md survives PDF reconciliation untouched.
4. Deleting the hand-authored .md removes its book from the index.
5. A transient absence (file moved away and back within the grace period)
   deletes nothing and does not trigger a re-chunk.
6. Deleting a whole shelf folder removes all of its books.
7. Final invariant: the books endpoint matches the files on disk exactly.

All effects are observed through HTTP endpoints only; the tests touch the
shared library folder because that is the user-facing input surface.
"""

import json
import os
import shutil
import time
from pathlib import Path

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

LIBRARY_DIR = Path("/app/cortex/library")

# Must match LIBRARY_RECONCILIATION_GRACE_SECONDS on the app container in
# the test_environments docker-compose files.
GRACE_SECONDS = int(os.getenv("LIBRARY_RECONCILIATION_GRACE_SECONDS", "15"))

# First ingestion includes PDF conversion and embedding-model warm-up.
INGEST_TIMEOUT = 1200  # seconds

# A full delete cascade is two grace periods (PDF layer, then MD layer)
# plus both scan intervals; generously padded.
RECONCILE_TIMEOUT = 300  # seconds

PDF_A = "shelf1/FashionDesigner.pdf"
MANUAL = "shelf1/manual.pdf"  # hand-authored .md, indexed under a .pdf path
PDF_TRANSIENT = "shelf2/lycanthropes-in-eberron.pdf"
PDF_SURVIVOR = "shelf3/FashionDesigner.pdf"

ALL_BOOKS = {PDF_A, MANUAL, PDF_TRANSIENT, PDF_SURVIVOR}


def _books() -> dict[str, dict]:
    """Return the books index keyed by file_path."""
    resp = requests.get(f"{BASE_URL}/private/v1/books")
    assert resp.status_code == 200, f"/private/v1/books: {resp.status_code}"
    return {b["file_path"]: b for b in resp.json()}


def _search(file_path: str) -> list[dict]:
    """Return search results filtered to *file_path* (empty when unindexed)."""
    resp = requests.post(
        f"{BASE_URL}/private/v1/search",
        json={"filter": {"file_path": file_path}, "top_k": 1},
        stream=True,
    )
    if resp.status_code != 200:
        return []
    parsed = [json.loads(line) for line in resp.iter_lines() if line]
    return [p for p in parsed if not p.get("done")]


def _wait_until(predicate, timeout: int, description: str) -> None:
    start = time.time()
    while not predicate():
        if time.time() - start > timeout:
            raise TimeoutError(f"{description} (waited {timeout}s)")
        time.sleep(3)


@pytest.mark.depends(on=["healthy"], name="baseline")
def test_baseline_ingested():
    """Every fixture book is indexed with chunks before reconciliation runs."""
    _wait_until(
        lambda: ALL_BOOKS <= set(_books()),
        INGEST_TIMEOUT,
        f"books endpoint never listed all of {sorted(ALL_BOOKS)}",
    )
    books = _books()
    for path in ALL_BOOKS:
        assert books[path]["chunk_count"] > 0, f"{path}: no chunks indexed"
    _wait_until(
        lambda: all(_search(path) for path in ALL_BOOKS),
        RECONCILE_TIMEOUT,
        "filtered search never returned results for every baseline book",
    )


@pytest.mark.depends(on=["baseline"], name="pdf_delete")
def test_pdf_delete_cascades():
    """Deleting a PDF removes its generated .md and its index entries."""
    (LIBRARY_DIR / PDF_A).unlink()

    generated_md = (LIBRARY_DIR / PDF_A).with_suffix(".md")
    _wait_until(
        lambda: not generated_md.exists(),
        RECONCILE_TIMEOUT,
        f"generated {generated_md.name} was not deleted after its PDF",
    )
    _wait_until(
        lambda: PDF_A not in _books(),
        RECONCILE_TIMEOUT,
        f"{PDF_A} still listed by /private/v1/books after deletion",
    )
    _wait_until(
        lambda: not _search(PDF_A),
        RECONCILE_TIMEOUT,
        f"search still returns chunks for deleted {PDF_A}",
    )

    # The same book on another shelf must be untouched.
    assert PDF_SURVIVOR in _books(), f"{PDF_SURVIVOR} was over-deleted"
    assert _search(PDF_SURVIVOR), f"{PDF_SURVIVOR} chunks were over-deleted"


@pytest.mark.depends(on=["pdf_delete"], name="manual_survives")
def test_hand_authored_md_survives():
    """PDF reconciliation must never delete hand-authored Markdown."""
    manual_md = LIBRARY_DIR / "shelf1" / "manual.md"
    assert manual_md.exists(), "hand-authored manual.md was deleted from disk"
    assert MANUAL in _books(), "hand-authored manual.md left the books index"
    assert _search(MANUAL), "hand-authored manual.md chunks were deleted"


@pytest.mark.depends(on=["manual_survives"], name="manual_delete")
def test_hand_authored_md_delete():
    """Deleting a hand-authored .md removes its book from the index."""
    (LIBRARY_DIR / "shelf1" / "manual.md").unlink()

    _wait_until(
        lambda: MANUAL not in _books(),
        RECONCILE_TIMEOUT,
        f"{MANUAL} still listed by /private/v1/books after deletion",
    )
    _wait_until(
        lambda: not _search(MANUAL),
        RECONCILE_TIMEOUT,
        f"search still returns chunks for deleted {MANUAL}",
    )


@pytest.mark.depends(on=["manual_delete"], name="transient")
def test_transient_absence_not_deleted():
    """A file that vanishes briefly (e.g. mid-sync) must not be reconciled."""
    pdf_path = LIBRARY_DIR / PDF_TRANSIENT
    md_path = pdf_path.with_suffix(".md")
    parked = Path("/tmp") / pdf_path.name

    results = _search(PDF_TRANSIENT)
    assert results, f"{PDF_TRANSIENT} not searchable before the transient move"
    completed_at_before = results[0].get("chunking_completed_at")

    shutil.move(str(pdf_path), str(parked))
    time.sleep(GRACE_SECONDS / 2)
    shutil.move(str(parked), str(pdf_path))

    # Watch for two full grace periods: nothing may disappear.
    deadline = time.time() + 2 * GRACE_SECONDS
    while time.time() < deadline:
        assert md_path.exists(), (
            f"{md_path.name} was deleted after a transient absence of "
            f"{GRACE_SECONDS / 2:.0f}s (grace is {GRACE_SECONDS}s)"
        )
        assert PDF_TRANSIENT in _books(), (
            f"{PDF_TRANSIENT} left the books index after a transient absence"
        )
        time.sleep(2)

    results = _search(PDF_TRANSIENT)
    assert results, f"{PDF_TRANSIENT} chunks were deleted"
    assert results[0].get("chunking_completed_at") == completed_at_before, (
        f"{PDF_TRANSIENT} was re-chunked after a transient absence even "
        "though its content never changed"
    )


@pytest.mark.depends(on=["transient"], name="shelf_delete")
def test_shelf_delete():
    """Deleting a whole shelf folder removes all of its books."""
    shutil.rmtree(LIBRARY_DIR / "shelf2")

    _wait_until(
        lambda: PDF_TRANSIENT not in _books(),
        RECONCILE_TIMEOUT,
        f"{PDF_TRANSIENT} still listed after its shelf was deleted",
    )
    _wait_until(
        lambda: not _search(PDF_TRANSIENT),
        RECONCILE_TIMEOUT,
        f"search still returns chunks for deleted shelf entry {PDF_TRANSIENT}",
    )


@pytest.mark.depends(on=["shelf_delete"])
def test_books_matches_disk_exactly():
    """The books index equals the files on disk — no stale extras, ever."""
    _wait_until(
        lambda: set(_books()) == {PDF_SURVIVOR},
        RECONCILE_TIMEOUT,
        f"books endpoint did not settle to exactly {{{PDF_SURVIVOR!r}}}: "
        f"got {sorted(_books())}",
    )
    assert _books()[PDF_SURVIVOR]["chunk_count"] > 0
    assert _search(PDF_SURVIVOR), f"{PDF_SURVIVOR} must still be searchable"
