"""PDF to Markdown conversion pipeline.

Runs as a background task at startup. Continuously scans the cortex library
folder for PDF files, converts new or changed PDFs to Markdown using
pymupdf4llm, and tracks state in Redis.

Status values per PDF:
  Checking   - hash is currently being compared
  Queued     - hash changed (or new file), awaiting conversion
  Converting - conversion in progress
  Converted  - up-to-date Markdown exists

A missing Redis entry means the file has never been seen before.
"""

import asyncio
import hashlib
import logging
import os
from datetime import datetime
from pathlib import Path

import pymupdf
import pymupdf4llm
import yaml
from common import CUSTOMIZATION_FOLDER
from redis_memory import Memory

logger = logging.getLogger(__name__)

LIBRARY_DIR = CUSTOMIZATION_FOLDER / "library"

PDF_CHECK_INTERVAL_SECONDS = int(
    os.environ.get("PDF_CHECK_INTERVAL_SECONDS", "5")
)

# Status constants
STATUS_CHECKING = "Checking"
STATUS_QUEUED = "Queued"
STATUS_CONVERTING = "Converting"
STATUS_CONVERTED = "Converted"


def _compute_hash(path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _get_state(memory: Memory) -> dict:
    """Return the pipeline state dict, initialising it if absent."""
    if not hasattr(memory, "pdf_pipeline_state"):
        memory.pdf_pipeline_state = {}
    return memory.pdf_pipeline_state


def _front_matter(pdf_path: Path) -> str:
    """Build YAML front matter from PDF metadata and path (blocking)."""
    doc = pymupdf.open(str(pdf_path))
    meta = doc.metadata
    doc.close()

    data = {
        "filename": pdf_path.stem,
        "tags": list(pdf_path.relative_to(LIBRARY_DIR).parent.parts),
        "title": meta.get("title") or "",
        "author": meta.get("author") or "",
    }
    return "---\n" + yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False) + "---\n\n"


def _convert(pdf_path: Path) -> str:
    """Convert a PDF to Markdown with YAML front matter prepended (blocking)."""
    return _front_matter(pdf_path) + pymupdf4llm.to_markdown(str(pdf_path))


async def run_pdf_pipeline() -> None:
    """Background loop: scan PDFs, convert changed ones, sleep, repeat."""
    logger.info(
        "PDF pipeline started. Watching: %s  (interval: %ss)",
        LIBRARY_DIR,
        PDF_CHECK_INTERVAL_SECONDS,
    )

    loop = asyncio.get_event_loop()

    while True:
        if not LIBRARY_DIR.exists():
            logger.debug(
                "PDF pipeline: library dir not found, skipping check."
            )
            await asyncio.sleep(PDF_CHECK_INTERVAL_SECONDS)
            continue

        pdf_files = sorted(LIBRARY_DIR.rglob("*.pdf"))
        logger.debug(
            "PDF pipeline: check running, %d PDF(s) found.", len(pdf_files)
        )

        # ── Phase 1: check hashes, mark Queued if changed/new ──────────────
        queued_paths: list[Path] = []

        for pdf_path in pdf_files:
            pdf_key = str(pdf_path)
            current_hash = _compute_hash(pdf_path)

            with Memory() as memory:
                state = _get_state(memory)
                entry = state.get(pdf_key) or {}
                stored_hash = entry.get("hash")

                # Mark as Checking while we examine this file
                state[pdf_key] = {**entry, "status": STATUS_CHECKING}
                memory.pdf_pipeline_state = state

            md_path = pdf_path.with_suffix(".md")
            output_missing = not md_path.exists()

            if current_hash != stored_hash:
                reason = "hash changed"
            elif output_missing:
                reason = "output file missing"
            else:
                reason = None

            if reason:
                with Memory() as memory:
                    state = _get_state(memory)
                    entry = state.get(pdf_key) or {}
                    state[pdf_key] = {
                        **entry,
                        "status": STATUS_QUEUED,
                        "hash": current_hash,
                    }
                    memory.pdf_pipeline_state = state

                queued_paths.append(pdf_path)
                logger.info(
                    "PDF pipeline: %s queued — %s.", pdf_path.name, reason
                )
            else:
                with Memory() as memory:
                    state = _get_state(memory)
                    entry = state.get(pdf_key) or {}
                    state[pdf_key] = {**entry, "status": STATUS_CONVERTED}
                    memory.pdf_pipeline_state = state

        # ── Phase 2: convert each queued PDF ────────────────────────────────
        for pdf_path in queued_paths:
            pdf_key = str(pdf_path)
            md_path = pdf_path.with_suffix(".md")
            start_dt = datetime.now()
            started_at = start_dt.isoformat()

            with Memory() as memory:
                state = _get_state(memory)
                entry = state.get(pdf_key) or {}
                state[pdf_key] = {
                    **entry,
                    "status": STATUS_CONVERTING,
                    "lastConversionStart": started_at,
                }
                memory.pdf_pipeline_state = state

            logger.info(
                "PDF pipeline: converting %s — started at %s",
                pdf_path.name,
                started_at,
            )

            # Blocking I/O — run in executor so the event loop stays free
            md_text = await loop.run_in_executor(None, _convert, pdf_path)
            md_path.write_text(md_text, encoding="utf-8")

            end_dt = datetime.now()
            completed_at = end_dt.isoformat()
            elapsed = (end_dt - start_dt).total_seconds()

            with Memory() as memory:
                state = _get_state(memory)
                entry = state.get(pdf_key) or {}
                state[pdf_key] = {
                    **entry,
                    "status": STATUS_CONVERTED,
                    "lastConversionComplete": completed_at,
                }
                memory.pdf_pipeline_state = state

            logger.info(
                "PDF pipeline: %s → %s — completed at %s (elapsed: %.1fs)",
                pdf_path.name,
                md_path.name,
                completed_at,
                elapsed,
            )

        await asyncio.sleep(PDF_CHECK_INTERVAL_SECONDS)
