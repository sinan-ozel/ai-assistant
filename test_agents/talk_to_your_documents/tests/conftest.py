"""Pytest configuration and fixtures for talk_to_your_documents tests."""

import shutil
from pathlib import Path

import pytest

# Both containers mount AGENT_FOLDER at /app/cortex and TEST_FOLDER at /tests.
LIBRARY_DIR = Path("/app/cortex/library")
FIXTURES_DIR = Path("/tests/fixtures")


@pytest.fixture(scope="session", autouse=True)
def library_setup():
    """Populate the library once per session; clean up after all tests finish.

    Removes any leftover state, recreates the shelf directories, and copies
    source PDFs from the test fixtures folder into the watched library so the
    pipeline starts from a known-clean state.  On teardown, removes the entire
    library directory (PDFs, generated Markdown files, and shelf folders).
    """
    if LIBRARY_DIR.exists():
        shutil.rmtree(LIBRARY_DIR)

    for shelf_dir in sorted(FIXTURES_DIR.iterdir()):
        if not shelf_dir.is_dir():
            continue
        target = LIBRARY_DIR / shelf_dir.name
        target.mkdir(parents=True)
        for pdf in shelf_dir.glob("*.pdf"):
            shutil.copy2(pdf, target / pdf.name)

    yield

    if LIBRARY_DIR.exists():
        shutil.rmtree(LIBRARY_DIR)
