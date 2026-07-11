"""Pytest configuration and fixtures for library_reconciliation tests.

The tests exercise the reconciliation logic that removes state, generated
Markdown, and vector-store chunks when files are deleted from the library.
They manipulate the shared library folder directly (the user-facing input
surface) and observe every effect through HTTP endpoints only.
"""

import shutil
from pathlib import Path

import pytest

# Both containers mount AGENT_FOLDER at /app/cortex and TEST_FOLDER at /tests.
LIBRARY_DIR = Path("/app/cortex/library")
FIXTURES_DIR = Path("/tests/fixtures")

# Library layout for the reconciliation scenarios:
#   shelf1/FashionDesigner.pdf          — deleted mid-session (PDF cascade)
#   shelf1/manual.md                    — hand-authored; deleted mid-session
#   shelf2/lycanthropes-in-eberron.pdf  — moved out and back (transient),
#                                         then removed with its whole shelf
#   shelf3/FashionDesigner.pdf          — survives everything (final check)
_LAYOUT = {
    "shelf1/FashionDesigner.pdf": "FashionDesigner.pdf",
    "shelf1/manual.md": "manual.md",
    "shelf2/lycanthropes-in-eberron.pdf": "lycanthropes-in-eberron.pdf",
    "shelf3/FashionDesigner.pdf": "FashionDesigner.pdf",
}


@pytest.fixture(scope="session", autouse=True)
def library_setup():
    """Populate the library once per session; clean up after all tests finish.

    Removes any leftover state, recreates the shelf directories, and copies
    source files from the test fixtures folder into the watched library so
    the pipelines start from a known-clean state.  On teardown, removes the
    entire library directory.
    """
    if LIBRARY_DIR.exists():
        shutil.rmtree(LIBRARY_DIR)

    for rel_target, fixture_name in _LAYOUT.items():
        target = LIBRARY_DIR / rel_target
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(FIXTURES_DIR / fixture_name, target)

    yield

    if LIBRARY_DIR.exists():
        shutil.rmtree(LIBRARY_DIR)
