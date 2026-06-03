"""Pytest configuration and fixtures for talk_to_your_documents tests."""

import os
import socket
from pathlib import Path

import lancedb
import pytest
import redis
from qdrant_client import QdrantClient

REDIS_HOST = os.getenv("REDIS_HOST", "redis-test")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant-test")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

# Path is the same in both the app and test containers because
# both mount CORTEX_FOLDER at /app/cortex.
LIBRARY_DIR = Path("/app/cortex/library")


def _is_hidden(path: Path) -> bool:
    """Return True if any component of *path* relative to LIBRARY_DIR starts with '.'."""
    return any(part.startswith(".") for part in path.parts[len(LIBRARY_DIR.parts):])


@pytest.fixture
def pdf_conversion_reset():
    """Reset the PDF pipeline state and remove Markdown files for visible PDFs.

    Clears the Redis pipeline state so every PDF is treated as new, then
    deletes the .md file next to each visible (non-hidden) PDF so the pipeline
    is forced to reconvert them. Hidden files and files inside hidden folders
    are left untouched.
    """
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.delete("memory:pdf_pipeline_state")

    for pdf in LIBRARY_DIR.rglob("*.pdf"):
        if _is_hidden(pdf):
            continue
        pdf.with_suffix(".md").unlink(missing_ok=True)

    yield


@pytest.fixture
def chunk_reset():
    """Reset the chunking pipeline state and drop all vector-store collections.

    Clears the Redis chunking state and the library index (memory.library) so
    every Markdown file is treated as new, then deletes all Qdrant collections
    when Qdrant is reachable (no-op when it is not).

    On teardown, restores any Markdown files that were modified during the test
    so the on-disk cortex folder is left in its original state.
    """


    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.delete("memory:chunking_pipeline_state")
    r.delete("memory:library")

    try:
        with socket.create_connection((QDRANT_HOST, QDRANT_PORT), timeout=2):
            qdrant_reachable = True
    except OSError:
        qdrant_reachable = False

    if qdrant_reachable:

        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        for c in client.get_collections().collections:
            client.delete_collection(c.name)
    else:

        lancedb_path = os.getenv("LANCEDB_PATH", "/app/data/lancedb")
        try:
            db = lancedb.connect(lancedb_path)
            for table_name in db.table_names():
                db.drop_table(table_name)
        except Exception:
            pass

    # Snapshot all visible Markdown files before the test runs
    snapshots: dict[Path, str] = {}
    for md in LIBRARY_DIR.rglob("*.md"):
        if not _is_hidden(md):
            try:
                snapshots[md] = md.read_text(encoding="utf-8")
            except OSError:
                pass

    yield

    # Restore any files that were modified or created during the test
    for md, original in snapshots.items():
        try:
            if md.read_text(encoding="utf-8") != original:
                md.write_text(original, encoding="utf-8")
        except OSError:
            pass


@pytest.fixture(scope="session", autouse=True)
def cleanup_markdown_files():
    """Delete all visible Markdown files in the library after the test session.

    Runs automatically at the end of every session so the on-disk cortex folder
    is left with only the original PDFs, regardless of which tests ran.
    """
    yield

    for md in LIBRARY_DIR.rglob("*.md"):
        if not _is_hidden(md):
            md.unlink(missing_ok=True)
