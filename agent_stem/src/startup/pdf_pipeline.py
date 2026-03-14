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
from pymupdf.mupdf import FzErrorLibrary
import yaml
from common import CUSTOMIZATION_FOLDER
from redis_memory import Memory

logger = logging.getLogger(__name__)

LIBRARY_DIR = CUSTOMIZATION_FOLDER / "library"

PDF_CHECK_INTERVAL_SECONDS = int(
    os.environ.get("PDF_CHECK_INTERVAL_SECONDS", "5")
)

OCR_WORDS_PER_PAGE_THRESHOLD = int(
    os.environ.get("OCR_WORDS_PER_PAGE_THRESHOLD", "50")
)

OCR_LANGUAGE = os.environ.get("OCR_LANGUAGE", "eng")

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



def _unique_top_level_header(md_text: str) -> str | None:
    """Return the text of the single top-level header, or None.

    Top-level means the header depth with the fewest '#' characters found
    in the document. If there is exactly one such header, its text is
    returned (without leading '#' characters or surrounding whitespace).
    """
    headers: list[tuple[int, str]] = []
    for line in md_text.splitlines():
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            headers.append((level, line.lstrip("#").strip()))

    if not headers:
        return None

    min_level = min(level for level, _ in headers)
    top_headers = [text for level, text in headers if level == min_level]

    return top_headers[0] if len(top_headers) == 1 else None


def _front_matter(
    pdf_path: Path,
    md_text: str,
    page_count: int = 0,
    ocr_used: bool = False,
) -> str:
    """Build YAML front matter from PDF metadata, path, and body (blocking)."""
    doc = pymupdf.open(str(pdf_path))
    meta = doc.metadata
    doc.close()

    data = {
        "filename": pdf_path.stem,
        "tags": list(pdf_path.relative_to(LIBRARY_DIR).parent.parts),
        "pdf_title": meta.get("title") or "",
        "pdf_author": meta.get("author") or "",
        "pages": page_count,
    }

    if ocr_used:
        data["ocr"] = True

    body_title = _unique_top_level_header(md_text)
    if body_title is not None:
        data["body_title"] = body_title

    return (
        "---\n"
        + yaml.dump(
            data, allow_unicode=True, default_flow_style=False, sort_keys=False
        )
        + "---\n\n"
    )


def _to_markdown_safe(pdf_path: Path, **kwargs) -> str:
    """Attempt pymupdf4llm.to_markdown, falling back to ignore_images=True
    on JPX decode errors, then page-by-page if that also fails.
    """
    try:
        return pymupdf4llm.to_markdown(str(pdf_path), **kwargs)
    except FzErrorLibrary as e:
        if "Failed to decode JPX image" not in str(e):
            raise

        logger.warning(
            "PDF pipeline: %s contains undecodable JPX image(s); "
            "retrying with ignore_images=True.",
            pdf_path.name,
        )
        try:
            return pymupdf4llm.to_markdown(str(pdf_path), ignore_images=True, **kwargs)
        except FzErrorLibrary as e2:
            if "Failed to decode JPX image" not in str(e2):
                raise

            logger.warning(
                "PDF pipeline: %s still failing with ignore_images=True; "
                "falling back to page-by-page conversion.",
                pdf_path.name,
            )
            return _convert_safe(pdf_path, **kwargs)


def _convert_safe(pdf_path: Path, **kwargs) -> str:
    """Last-resort page-by-page conversion, skipping pages that raise
    JPX decode errors. Each skipped page is logged with filename and number.
    """
    doc = pymupdf.open(str(pdf_path))
    page_count = doc.page_count
    doc.close()

    pages = []
    for pno in range(page_count):
        try:
            page_md = pymupdf4llm.to_markdown(
                str(pdf_path), pages=[pno], ignore_images=True, **kwargs
            )
            pages.append(page_md)
        except FzErrorLibrary as e:
            if "Failed to decode JPX image" not in str(e):
                raise
            logger.warning(
                "PDF pipeline: skipping page %d of %s due to JPX decode error.",
                pno,
                pdf_path.name,
            )
            pages.append(f"\n\n[Page {pno} skipped — JPX image decode error]\n\n")

    return "".join(pages)


def _convert(pdf_path: Path) -> str:
    """Convert a PDF to Markdown with YAML front matter prepended
    (blocking).

    Performs a two-pass conversion: the first pass uses standard text
    extraction. If the output looks image-based (too few words per page),
    a second pass runs with Tesseract OCR enabled.

    Both passes gracefully handle JPX image decode errors via fallback
    strategies, because some PDFs simply cannot be trusted.
    """
    md_text = _to_markdown_safe(pdf_path)

    doc = pymupdf.open(str(pdf_path))
    page_count = doc.page_count
    doc.close()

    ocr_used = False
    if page_count > 0:
        words_per_page = len(md_text.split()) / page_count
        if words_per_page < OCR_WORDS_PER_PAGE_THRESHOLD:
            logger.info(
                "PDF pipeline: %s looks image-based (%.1f words/page),"
                " retrying with OCR (language: %s).",
                pdf_path.name,
                words_per_page,
                OCR_LANGUAGE,
            )
            md_text = _to_markdown_safe(
                pdf_path,
                use_ocr=True,
                ocr_language=OCR_LANGUAGE,
            )
            ocr_used = True

    return _front_matter(pdf_path, md_text, page_count=page_count, ocr_used=ocr_used) + md_text


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
            logger.debug("PDF pipeline: library dir not found, skipping check.")
            await asyncio.sleep(PDF_CHECK_INTERVAL_SECONDS)
            continue

        pdf_files = sorted(
            p for p in LIBRARY_DIR.rglob("*.pdf")
            if not any(part.startswith(".") for part in p.parts[len(LIBRARY_DIR.parts):])
        )
        logger.debug(
            "PDF pipeline: check running, %d PDF(s) found.", len(pdf_files)
        )

        # ── Phase 1: check hashes, mark Queued if changed/new ──────────────
        queued_paths: list[Path] = []

        for pdf_path in pdf_files:
            pdf_key = str(pdf_path)
            current_hash = _compute_hash(pdf_path)

            with Memory() as memory:
                if not hasattr(memory, "pdf_pipeline_state"):
                    memory.pdf_pipeline_state = {}
                entry = memory.pdf_pipeline_state.get(pdf_key) or {}
                stored_hash = entry.get("hash")

                # Mark as Checking while we examine this file
                memory.pdf_pipeline_state[pdf_key] = {**entry, "status": STATUS_CHECKING}

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
                    if not hasattr(memory, "pdf_pipeline_state"):
                        memory.pdf_pipeline_state = {}
                    entry = memory.pdf_pipeline_state.get(pdf_key) or {}
                    memory.pdf_pipeline_state[pdf_key] = {
                        **entry,
                        "status": STATUS_QUEUED,
                        "hash": current_hash,
                    }

                queued_paths.append(pdf_path)
                logger.info(
                    "PDF pipeline: %s queued — %s.", pdf_path.name, reason
                )
            else:
                with Memory() as memory:
                    if not hasattr(memory, "pdf_pipeline_state"):
                        memory.pdf_pipeline_state = {}
                    entry = memory.pdf_pipeline_state.get(pdf_key) or {}
                    memory.pdf_pipeline_state[pdf_key] = {**entry, "status": STATUS_CONVERTED}

        # ── Phase 2: convert each queued PDF ────────────────────────────────
        for pdf_path in queued_paths:
            pdf_key = str(pdf_path)
            md_path = pdf_path.with_suffix(".md")
            start_dt = datetime.now()
            started_at = start_dt.isoformat()

            with Memory() as memory:
                if not hasattr(memory, "pdf_pipeline_state"):
                    memory.pdf_pipeline_state = {}
                entry = memory.pdf_pipeline_state.get(pdf_key) or {}
                memory.pdf_pipeline_state[pdf_key] = {
                    **entry,
                    "status": STATUS_CONVERTING,
                    "lastConversionStart": started_at,
                }

            logger.info(
                "PDF pipeline: converting %s — started at %s",
                pdf_path.name,
                started_at,
            )

            # Blocking I/O — run in executor so the event loop stays free
            try:
                md_text = await loop.run_in_executor(None, _convert, pdf_path)
                md_path.write_text(md_text, encoding="utf-8")
            except pymupdf.mupdf.FzErrorLibrary as e:
                logger.error(
                    "PDF pipeline: failed to convert %s — %s: %s",
                    pdf_path.name,
                    type(e).__name__,
                    e,
                )
                continue

            end_dt = datetime.now()
            completed_at = end_dt.isoformat()
            elapsed = (end_dt - start_dt).total_seconds()

            with Memory() as memory:
                if not hasattr(memory, "pdf_pipeline_state"):
                    memory.pdf_pipeline_state = {}
                entry = memory.pdf_pipeline_state.get(pdf_key) or {}
                memory.pdf_pipeline_state[pdf_key] = {
                    **entry,
                    "status": STATUS_CONVERTED,
                    "lastConversionComplete": completed_at,
                }

            logger.info(
                "PDF pipeline: %s → %s — completed at %s (elapsed: %.1fs)",
                pdf_path.name,
                md_path.name,
                completed_at,
                elapsed,
            )

        await asyncio.sleep(PDF_CHECK_INTERVAL_SECONDS)
