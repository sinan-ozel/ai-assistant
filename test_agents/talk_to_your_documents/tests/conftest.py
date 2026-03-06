"""Pytest configuration and fixtures for talk_to_your_documents tests."""

import os
from pathlib import Path

import pytest
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis-test")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Path is the same in both the app and test containers because
# both mount CORTEX_FOLDER at /app/cortex.
LIBRARY_DIR = Path("/app/cortex/library")


@pytest.fixture
def pdf_conversion_reset():
    """Reset the PDF pipeline state and remove all existing Markdown outputs.

    Clears the Redis pipeline state so every PDF is treated as new,
    then deletes all .md files that sit alongside PDFs in the library.
    Yields the list of expected Markdown paths for the test to poll.
    """
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.delete("memory:pdf_pipeline_state")

    md_files = [p.with_suffix(".md") for p in sorted(LIBRARY_DIR.rglob("*.pdf"))]
    for md in md_files:
        md.unlink(missing_ok=True)

    yield md_files
