"""PDF to Markdown conversion pipeline.

Runs as a background task at startup. Continuously scans the cortex library
folder for PDF files, converts new or changed PDFs to Markdown using
pymupdf4llm, and tracks state in Redis via a SyncedDict.

Status values per PDF:
  Checking   - hash is currently being compared
  Queued     - hash changed (or new file), awaiting conversion
  Converting - conversion in progress
  Converted  - up-to-date Markdown exists
  Missing    - file vanished from disk; reconciliation grace period running

A missing state entry means the file has never been seen before.

PDFs are the source of truth for the Markdown files this pipeline generates:
when a PDF stays missing past the reconciliation grace period, its state
entry and its generated .md are removed (hand-authored .md files are left
alone), which in turn lets the chunking pipeline reconcile the vector store.
"""

import asyncio
import hashlib
import logging
import os
import re
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import pymupdf
import pymupdf4llm
import yaml
from common import CUSTOMIZATION_FOLDER
from pymupdf.mupdf import FzErrorLibrary
from synced_memory import Memory, SyncedDict

logger = logging.getLogger(__name__)

LIBRARY_DIR = CUSTOMIZATION_FOLDER / "library"

PDF_CHECK_INTERVAL_SECONDS = int(
    os.environ.get("PDF_CHECK_INTERVAL_SECONDS", "5")
)

OCR_WORDS_PER_PAGE_THRESHOLD = int(
    os.environ.get("OCR_WORDS_PER_PAGE_THRESHOLD", "50")
)

OCR_LANGUAGE = os.environ.get("OCR_LANGUAGE", "eng")

# Fraction of U+FFFD replacement characters in extracted text above which the
# text layer is considered garbled (broken font-to-Unicode mapping in the PDF)
# and conversion is retried with OCR.
GARBLED_CHAR_RATIO_THRESHOLD = float(
    os.environ.get("GARBLED_CHAR_RATIO_THRESHOLD", "0.002")
)

# How long a file must stay missing from disk before its derived artifacts
# (generated Markdown, state entries) are removed. The grace period protects
# against transient absences, e.g. a file-sync tool moving files mid-scan.
RECONCILIATION_GRACE_SECONDS = int(
    os.environ.get("LIBRARY_RECONCILIATION_GRACE_SECONDS", "60")
)

# Status constants
STATUS_CHECKING = "Checking"
STATUS_QUEUED = "Queued"
STATUS_CONVERTING = "Converting"
STATUS_CONVERTED = "Converted"
STATUS_MISSING = "Missing"

_state_memory = Memory()
if not hasattr(_state_memory, "pdf_pipeline_state"):
    _state_memory.pdf_pipeline_state = {}
_pdf_pipeline_state: SyncedDict = _state_memory.pdf_pipeline_state

# PyMuPDF/Tesseract are C extensions that do not release the GIL during
# rendering or OCR, so running _convert() in a thread executor still stalls
# every other coroutine (health checks included) for the full page-by-page
# conversion time. A separate process gives the event loop its own GIL.
_pdf_conversion_pool = ProcessPoolExecutor(max_workers=1)


def _compute_hash(path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _unique_top_level_header(md_text: str) -> str | None:
    """Return the text of the single top-level header, or None.

    Top-level means the header depth with the fewest '#' characters found in
    the document. If there is exactly one such header, its text is returned
    (without leading '#' characters or surrounding whitespace).
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
        # Marks this file as pipeline output so reconciliation can delete it
        # when its source PDF is removed; hand-authored Markdown lacks the
        # marker and is never deleted.
        "converted_from_pdf": True,
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
    """Attempt pymupdf4llm.to_markdown, falling back to ignore_images=True on
    JPX decode errors, then page-by-page if that also fails."""
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
            return pymupdf4llm.to_markdown(
                str(pdf_path), ignore_images=True, **kwargs
            )
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
    """Last-resort page-by-page conversion, skipping pages that raise JPX
    decode errors.

    Each skipped page is logged with filename and number.
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
            pages.append(
                f"\n\n[Page {pno} skipped — JPX image decode error]\n\n"
            )

    return "".join(pages)


def _garbled_ratio(text: str) -> float:
    """Return the fraction of U+FFFD replacement characters in *text*.

    PDFs with a broken or missing ToUnicode CMap (common in older books with
    subset fonts) extract some glyphs — most often the space glyph — as U+FFFD,
    producing text like ``C�r�e�a�t�u�r�e�s``.
    """
    if not text:
        return 0.0
    return text.count("�") / len(text)


def _scrub_replacement_chars(md_text: str, pdf_name: str) -> str:
    """Replace any remaining U+FFFD runs with a single space.

    Last-resort cleanup after conversion (and the OCR retry, if it ran): the
    replacement characters carry no information and poison chunking, embedding,
    and search results downstream. Each run of U+FFFD plus any adjacent spaces
    collapses to one space so ordinary indentation elsewhere in the document is
    left untouched.
    """
    count = md_text.count("�")
    if not count:
        return md_text
    logger.warning(
        "PDF pipeline: %s — %d unmappable glyph(s) (U+FFFD) remain after "
        "conversion; replacing with spaces. The source PDF has a broken "
        "font-to-Unicode mapping; extracted text quality may be degraded.",
        pdf_name,
        count,
    )
    return re.sub(r"[ \t]*�[ \t�]*", " ", md_text)


def _convert(pdf_path: Path) -> str:
    """Convert a PDF to Markdown with YAML front matter prepended (blocking).

    Performs a two-pass conversion: the first pass uses standard text
    extraction. If the output looks image-based (too few words per page) or
    garbled (too many U+FFFD replacement characters from a broken
    font-to-Unicode mapping), a second pass runs with Tesseract OCR enabled.
    Any replacement characters that survive both passes are scrubbed so they
    never reach the chunking pipeline.

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
        garbled_ratio = _garbled_ratio(md_text)
        if words_per_page < OCR_WORDS_PER_PAGE_THRESHOLD:
            ocr_reason = f"looks image-based ({words_per_page:.1f} words/page)"
        elif garbled_ratio > GARBLED_CHAR_RATIO_THRESHOLD:
            ocr_reason = (
                f"text layer is garbled ({garbled_ratio:.2%} replacement "
                f"characters — broken font-to-Unicode mapping)"
            )
        else:
            ocr_reason = None

        if ocr_reason:
            logger.info(
                "PDF pipeline: %s %s, retrying with OCR (language: %s).",
                pdf_path.name,
                ocr_reason,
                OCR_LANGUAGE,
            )
            md_text = _to_markdown_safe(
                pdf_path,
                use_ocr=True,
                ocr_language=OCR_LANGUAGE,
            )
            ocr_used = True

    md_text = _scrub_replacement_chars(md_text, pdf_path.name)

    return (
        _front_matter(
            pdf_path, md_text, page_count=page_count, ocr_used=ocr_used
        )
        + md_text
    )


def _is_generated_markdown(md_path: Path) -> bool:
    """Return True if *md_path* was written by this pipeline.

    Detected via the ``converted_from_pdf`` front-matter marker, falling back
    to the presence of the ``pdf_title`` key for files generated before the
    marker existed. Hand-authored Markdown returns False and must never be
    deleted by reconciliation.
    """
    yaml_lines: list[str] = []
    try:
        with open(md_path, encoding="utf-8") as f:
            if f.readline().strip() != "---":
                return False
            for line in f:
                if line.strip() == "---":
                    break
                yaml_lines.append(line)
    except OSError:
        return False

    try:
        meta = yaml.safe_load("".join(yaml_lines)) or {}
    except yaml.YAMLError:
        return False

    if not isinstance(meta, dict):
        return False
    return bool(meta.get("converted_from_pdf")) or "pdf_title" in meta


def _reconcile_deleted_pdfs(pdf_files: list[Path]) -> None:
    """Remove state and generated Markdown for PDFs deleted from the library.

    Two-phase tombstone: a state entry whose PDF is no longer on disk is
    first marked ``Missing`` with a timestamp; only when a later scan still
    finds it missing after ``RECONCILIATION_GRACE_SECONDS`` are the state
    entry and the generated .md removed. The grace period protects against
    transient absences (e.g. a file-sync tool moving files mid-scan), and
    entries currently ``Converting`` are skipped until the work settles.

    Deleting the generated .md is what cascades the cleanup: the chunking
    pipeline's own reconciliation then removes the vector-store chunks.
    """
    on_disk = {str(p) for p in pdf_files}
    now = datetime.now(timezone.utc)

    for pdf_key in list(_pdf_pipeline_state.keys()):
        if pdf_key in on_disk:
            continue

        entry = dict(_pdf_pipeline_state.get(pdf_key) or {})
        if entry.get("status") == STATUS_CONVERTING:
            continue

        missing_since = entry.get("missingSince")
        if not missing_since:
            _pdf_pipeline_state[pdf_key] = {
                **entry,
                "status": STATUS_MISSING,
                "missingSince": now.isoformat(),
            }
            logger.info(
                "PDF pipeline: %s missing from disk — grace period "
                "started (%ss).",
                Path(pdf_key).name,
                RECONCILIATION_GRACE_SECONDS,
            )
            continue

        try:
            elapsed = (
                now - datetime.fromisoformat(missing_since)
            ).total_seconds()
        except ValueError:
            _pdf_pipeline_state[pdf_key] = {
                **entry,
                "missingSince": now.isoformat(),
            }
            continue
        if elapsed < RECONCILIATION_GRACE_SECONDS:
            continue

        md_path = Path(pdf_key).with_suffix(".md")
        if md_path.exists() and _is_generated_markdown(md_path):
            try:
                md_path.unlink()
                logger.info(
                    "PDF pipeline: deleted generated %s — source PDF was "
                    "removed %.0fs ago.",
                    md_path.name,
                    elapsed,
                )
            except OSError as e:
                logger.error(
                    "PDF pipeline: could not delete generated %s: %s — "
                    "will retry next scan.",
                    md_path.name,
                    e,
                )
                continue

        del _pdf_pipeline_state[pdf_key]
        logger.info(
            "PDF pipeline: reconciled deleted %s — state entry removed.",
            Path(pdf_key).name,
        )


def _scan_and_queue_pdfs(library_dir: Path) -> list[Path]:
    """Phase 1 (sync): find PDFs, hash-check, update state.

    Returns the list of PDF paths that need conversion.  Runs entirely in a
    thread executor so the event loop stays responsive while file I/O
    operations block.  Finishes by reconciling state entries whose PDFs were
    deleted from the library.
    """
    pdf_files = sorted(
        p
        for p in library_dir.rglob("*.pdf")
        if not any(
            part.startswith(".") for part in p.parts[len(library_dir.parts) :]
        )
    )
    logger.debug(
        "PDF pipeline: scan starting — %d PDF(s) found, %d state entries.",
        len(pdf_files),
        len(_pdf_pipeline_state),
    )

    queued_paths: list[Path] = []

    for pdf_path in pdf_files:
        pdf_key = str(pdf_path)
        current_hash = _compute_hash(pdf_path)

        entry = dict(_pdf_pipeline_state.get(pdf_key) or {})
        stored_hash = entry.get("hash")

        # The file is on disk, so any reconciliation tombstone is stale.
        entry.pop("missingSince", None)

        _pdf_pipeline_state[pdf_key] = {**entry, "status": STATUS_CHECKING}

        md_path = pdf_path.with_suffix(".md")
        output_missing = not md_path.exists()

        if current_hash != stored_hash:
            reason = "hash changed"
        elif output_missing:
            reason = "output file missing"
        else:
            reason = None

        if reason:
            _pdf_pipeline_state[pdf_key] = {
                **dict(_pdf_pipeline_state.get(pdf_key, {})),
                "status": STATUS_QUEUED,
                "hash": current_hash,
            }
            queued_paths.append(pdf_path)
            logger.info(
                "PDF pipeline: %s queued — %s " "(stored=%s current=%s).",
                pdf_path.name,
                reason,
                stored_hash[:8] if stored_hash else None,
                current_hash[:8],
            )
        else:
            _pdf_pipeline_state[pdf_key] = {
                **dict(_pdf_pipeline_state.get(pdf_key, {})),
                "status": STATUS_CONVERTED,
            }
            logger.debug(
                "PDF pipeline: %s up to date (hash=%s).",
                pdf_path.name,
                current_hash[:8],
            )

    try:
        _reconcile_deleted_pdfs(pdf_files)
    except Exception as e:
        logger.error(
            "PDF pipeline: reconciliation failed: %s — queued conversions "
            "proceed; reconciliation retries next scan.",
            e,
            exc_info=True,
        )

    return queued_paths


async def _convert_and_store_pdf(pdf_path: Path) -> None:
    """Phase 2: convert one PDF and update state.

    The Redis state writes run directly on the event loop (small, fast round
    trips); the actual conversion runs in ``_pdf_conversion_pool`` so GIL-
    holding OCR work can't stall the event loop. Raises on conversion errors so
    the caller can log and skip to the next file.
    """
    pdf_key = str(pdf_path)
    md_path = pdf_path.with_suffix(".md")
    start_dt = datetime.now()
    started_at = start_dt.isoformat()

    _pdf_pipeline_state[pdf_key] = {
        **dict(_pdf_pipeline_state.get(pdf_key) or {}),
        "status": STATUS_CONVERTING,
        "lastConversionStart": started_at,
    }

    logger.info(
        "PDF pipeline: converting %s — started at %s",
        pdf_path.name,
        started_at,
    )

    loop = asyncio.get_event_loop()
    md_text = await loop.run_in_executor(
        _pdf_conversion_pool, _convert, pdf_path
    )
    md_path.write_text(md_text, encoding="utf-8")

    end_dt = datetime.now()
    completed_at = end_dt.isoformat()
    elapsed = (end_dt - start_dt).total_seconds()

    _pdf_pipeline_state[pdf_key] = {
        **dict(_pdf_pipeline_state.get(pdf_key) or {}),
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

        # ── Phase 1: scan & queue — all blocking I/O runs in a thread ───────
        try:
            queued_paths = await loop.run_in_executor(
                None, _scan_and_queue_pdfs, LIBRARY_DIR
            )
        except Exception as e:
            logger.error(
                "PDF pipeline: scan phase failed: %s", e, exc_info=True
            )
            await asyncio.sleep(PDF_CHECK_INTERVAL_SECONDS)
            continue

        # ── Phase 2: convert each queued PDF (conversion runs in a process) ──
        for pdf_path in queued_paths:
            try:
                await _convert_and_store_pdf(pdf_path)
            except pymupdf.mupdf.FzErrorLibrary as e:
                logger.error(
                    "PDF pipeline: failed to convert %s — %s: %s",
                    pdf_path.name,
                    type(e).__name__,
                    e,
                )
            except Exception as e:
                logger.error(
                    "PDF pipeline: failed to convert %s — %s: %s",
                    pdf_path.name,
                    type(e).__name__,
                    e,
                    exc_info=True,
                )

        await asyncio.sleep(PDF_CHECK_INTERVAL_SECONDS)
