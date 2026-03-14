"""Markdown to vector chunk pipeline.

Runs as a background task at startup. Continuously scans the cortex library
folder for Markdown files, chunks new or changed ones using semantic
heading-based segmentation, and stores the resulting vectors in Qdrant (if
reachable) or LanceDB as a local fallback.

Status values per Markdown file:
  Checking  - mtime is currently being compared against the last chunk time
  Queued    - file is newer than last chunking_completed_at, awaiting processing
  Chunking  - chunking in progress
  Chunked   - up-to-date chunks exist in the vector store

A missing Redis entry means the file has never been processed before.
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import socket
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import tiktoken
import yaml
from common import CUSTOMIZATION_FOLDER
from redis_memory import Memory

logger = logging.getLogger(__name__)

LIBRARY_DIR = CUSTOMIZATION_FOLDER / "library"

CHUNK_CHECK_INTERVAL_SECONDS = int(
    os.environ.get("CHUNK_CHECK_INTERVAL_SECONDS", "10")
)

# Qdrant connection settings
QDRANT_HOST = os.environ.get("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION", "library")

# LanceDB path (used when Qdrant is not reachable)
LANCEDB_PATH = os.environ.get("LANCEDB_PATH", "/app/data/lancedb")
LANCEDB_TABLE = os.environ.get("LANCEDB_TABLE", "library")

# HuggingFace embedding model — baked into the container image at build time.
# bge-small-en-v1.5 is compact (133 MB) and produces 384-dimensional vectors.
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
EMBEDDING_DIM = 384  # output dimension of bge-small-en-v1.5

# Tiktoken encoder for token counting (cl100k_base covers GPT-3.5/4 vocab)
_tokenizer = tiktoken.get_encoding("cl100k_base")

# Status constants — mirror the naming convention in pdf_pipeline
STATUS_CHECKING = "Checking"
STATUS_QUEUED = "Queued"
STATUS_CHUNKING = "Chunking"
STATUS_CHUNKED = "Chunked"

# Lazy-loaded SentenceTransformer — imported and instantiated on first use
# so that startup does not block when the model is not needed yet.
_embedder = None


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _count_tokens(text: str) -> int:
    """Return the approximate token count for *text* using cl100k_base."""
    return len(_tokenizer.encode(text))


def _get_embedder():
    """Return the shared SentenceTransformer instance (loaded once, lazily)."""
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer

        logger.info("Chunking pipeline: loading embedding model %s.", EMBEDDING_MODEL)
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("Chunking pipeline: embedding model loaded.")
    return _embedder


def _qdrant_reachable(
    host: str = QDRANT_HOST,
    port: int = QDRANT_PORT,
    timeout: float = 2.0,
) -> bool:
    """Return True if a TCP connection to *host:port* can be established.

    Used to decide at write time whether to target Qdrant or fall back to
    LanceDB — avoids a hard dependency on Qdrant being present.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _chunking_ok(stats: dict) -> bool:
    """Return True if the chunking result looks reasonable.

    Flags a result as insufficient when:

    * fewer than 2 chunks were produced (suggests the heading detector found
      nothing), or
    * more than half of all chunks are empty (body-less placeholder chunks).
    """
    total = stats.get("total_chunks", 0)
    if total < 2:
        return False
    empty = stats.get("empty_chunks", 0)
    return (empty / total) < 0.5


def _deterministic_uuid(source_key: str, idx: int) -> str:
    """Return a stable UUID string for chunk *idx* of *source_key*.

    Uses MD5 so the result fits in 16 bytes and can be formatted as a UUID.
    Qdrant and LanceDB both accept UUID-format strings as point/row IDs.
    """
    digest = hashlib.md5(f"{source_key}::{idx}".encode()).hexdigest()
    return str(uuid.UUID(digest))


def _safe_json(obj) -> str:
    """JSON-serialise *obj* to a string for flat storage columns.

    LanceDB stores structured metadata as JSON strings when there is no
    native nested-struct schema defined up front.
    """
    return json.dumps(obj, ensure_ascii=False, default=str)


# ---------------------------------------------------------------------------
# MarkdownChunker — all parsing / chunking logic in one testable class
# ---------------------------------------------------------------------------


class MarkdownChunker:
    """Semantic chunker and parser for PDF-extracted / Markdown documents.

    All regex constants and parsing methods live here so that unit tests can
    exercise them independently of the I/O and vector-store machinery defined
    at module level.

    Typical usage::

        meta, body = MarkdownChunker.parse_frontmatter(text)
        toc, body  = MarkdownChunker.extract_toc_and_body(body)
        chunks     = MarkdownChunker.chunk_markdown(body, meta, toc)
    """

    # ------------------------------------------------------------------
    # Compiled regular expressions (class-level constants)
    # ------------------------------------------------------------------

    # ATX headers: # through ######
    HEADER_RE = re.compile(r"^(#{1,6})\s+(.+)$")

    # General word matcher (used in token-counting helpers if needed)
    WORD_RE = re.compile(r"\w+")

    # Accept many "dot leader" variants found in PDF-extracted TOCs
    LEADER = r"[.\u2026·•_\- ]{3,}"

    # Match a TOC entry line such as:
    #   "**Chapter 1: Discovering Eberron................................. 7**"
    # Captures: title (text before leaders/spaces) and page (1–4 digits)
    TOC_LINE_RE = re.compile(
        r"^\s*\**(?P<title>.+?)\**(?:[.\-–—·•\s]{2,})?(?P<page>\d{1,4})\s*$"
    )

    # Standalone bold title — **Title** on its own line, nothing else after
    BOLD_TITLE_RE = re.compile(r"^\*\*(.+?)\*\*\s*$")

    # Standalone italic title — _Title_ on its own line
    ITALIC_TITLE_RE = re.compile(r"^_(.+?)_\s*$")

    # Footer: bold page number — **12**
    FOOTER_PAGE_RE = re.compile(r"^\*\*(\d{1,4})\*\*\s*$")

    # Bare integer on its own line — plain page number
    BARE_NUMBER_RE = re.compile(r"^(\d{1,4})\s*$")

    # Markdown table row
    TABLE_RE = re.compile(r"^\|.+\|")

    # Chapter footer line such as "Chapter 1  |  Discovering Eberron"
    CHAPTER_FOOTER_RE = re.compile(r"^Chapter\s+\d+\s+\|.+$", re.IGNORECASE)

    # Chapter heading pattern — matches common chapter designations across
    # several languages; used to distinguish chapter entries in the TOC
    CHAPTER_RE = re.compile(
        r"\b(chapter|chap|ch|cap[ií]tulo|capitulo|capitolo|chapitre|"
        r"kapitel|глава|第\s*\d+\s*章)\.?\s*(\d+)",
        re.IGNORECASE,
    )

    # Drop cap: a 1–2 character decorative initial, optionally backtick-wrapped
    # e.g.  `W`  `Y`  W  F  (common artefact of PDF-to-Markdown conversion)
    DROP_CAP_RE = re.compile(r"^`?.{1,2}`?\s*$")

    # Sentence-ending punctuation — lines ending with these are prose, not titles
    SENTENCE_END_RE = re.compile(r'[.!?",\-—]\s*$')

    # Prose lead-in: **Bold word(s).** followed by more text on the same line
    BOLD_LEADIN_RE = re.compile(r"^\*\*.+?\*\*\s+\S")

    # Code block fence
    CODE_FENCE_RE = re.compile(r"^```")

    # Standalone page number — same semantics as BARE_NUMBER_RE, kept for
    # readability when used in a page-detection context
    PAGE_RE = re.compile(r"^\s*(\d+)\s*$")

    # Maximum plausible title length — real section titles are rarely longer
    MAX_TITLE_LEN = 80

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    def parse_frontmatter(text: str) -> tuple[dict, str]:
        """Parse YAML front matter from a Markdown string.

        Expects the text to optionally begin with a ``---`` fence.  When no
        front matter is found, returns an empty dict and the full text
        unchanged so callers can always destructure safely.

        Parameters
        ----------
        text:
            Full Markdown document, possibly starting with ``---``.

        Returns
        -------
        tuple[dict, str]
            ``(metadata_dict, body_text)`` where *body_text* is everything
            after the closing ``---`` fence.
        """
        lines = text.splitlines()
        if not lines or lines[0].strip() != "---":
            # No front-matter opener — return empty meta and the full text
            return {}, text

        i = 1
        yaml_lines: list[str] = []

        # Accumulate YAML content until the closing --- delimiter
        while i < len(lines) and lines[i].strip() != "---":
            yaml_lines.append(lines[i])
            i += 1

        # Everything after the closing --- is the document body
        body = "\n".join(lines[i + 1 :])
        meta = yaml.safe_load("\n".join(yaml_lines)) or {}

        return meta, body

    @staticmethod
    def extract_toc_and_body(text: str) -> tuple[list, str]:
        """Extract a Table of Contents and the body text that follows it.

        Detection is heuristic: at least 3 consecutive lines must match the
        TOC entry pattern before TOC mode is committed.  Once started, the
        TOC ends after 5 consecutive non-matching non-blank lines, or after
        the first 1 000 lines of the document.

        If no TOC is confidently detected, the full text is returned unchanged
        as the body so downstream processing is not disrupted.

        Parameters
        ----------
        text:
            Markdown document body (front matter already stripped).

        Returns
        -------
        tuple[list[dict], str]
            ``(toc_entries, body_text)`` where each TOC entry is a dict with
            keys ``title`` (str), ``page`` (int), and ``chapter`` (int|None).
        """
        lines = text.splitlines()
        toc: list[dict] = []
        toc_end_idx = 0
        consecutive_matches = 0
        toc_started = False
        failures = 0
        # Stop the TOC after this many consecutive non-matching non-blank lines
        max_failures = 5
        max_lines_to_search = min(1000, len(lines))

        for i, raw in enumerate(lines[:max_lines_to_search]):
            # Strip markdown emphasis markers before matching so that e.g.
            # "**Introduction...............3**" matches correctly
            line = raw.strip().strip("*_`")
            if not line:
                continue

            m = MarkdownChunker.TOC_LINE_RE.match(line)
            if m:
                consecutive_matches += 1
                # Require 3 consecutive hits before we commit to TOC mode to
                # avoid mis-classifying a stray numbered line early in the doc
                if consecutive_matches >= 3:
                    toc_started = True

                if toc_started:
                    title = m.group("title").strip()
                    page = int(m.group("page"))
                    # Try to extract a chapter number embedded in the title
                    ch_match = MarkdownChunker.CHAPTER_RE.search(title)
                    chapter = int(ch_match.group(2)) if ch_match else None

                    toc.append({"title": title, "page": page, "chapter": chapter})
                    toc_end_idx = i + 1
                    failures = 0
            else:
                consecutive_matches = 0
                if toc_started:
                    failures += 1
                    if failures > max_failures:
                        # Too many misses — the TOC is over
                        break

        # No confidently-detected TOC — return the full text unchanged
        if not toc_started:
            return [], text

        body = "\n".join(lines[toc_end_idx:])
        return toc, body

    @staticmethod
    def chunk_markdown(
        text: str,
        book_meta: dict,
        toc: list,
    ) -> list[dict]:
        """Semantic chunker for PDF-extracted / Markdown documents.

        Strategy
        --------
        **Pass 1** — classify every line as one of:

        * *heading* — ATX (``#``–``######``), standalone bold ``**Title**``,
          or standalone italic ``_Title_``
        * *footer* — bold page number ``**12**``, bare integer on its own line,
          or a "Chapter N | …" chapter footer
        * *body* — everything else

        Page numbers from footer lines are validated:

        * must be strictly increasing (protects against content numbers being
          mis-read as page numbers)
        * must not exceed ``book_meta["pages"]`` when that field is present

        **Pass 2** — walk the classified lines and emit a new chunk whenever a
        heading is encountered.  Each chunk carries:

        * ``text``     — the body text belonging to that section (stripped)
        * ``metadata`` — ``title``, ``toc_title``, ``chapter``, ``tags``,
          ``page``, ``tokens``, ``parent_index``, ``hierarchy``, ``book``,
          ``chunking_started_at``, ``chunking_completed_at`` (last two are
          ``None`` here and stamped by the caller after all chunks are ready)

        TOC entries matching ``CHAPTER_RE`` are reserved for the ``chapter``
        field only; they do not influence ``toc_title`` or page-range
        narrowing, which are unreliable when chapter entries share pages with
        section entries.

        Parameters
        ----------
        text:
            Markdown body text (front matter and TOC already stripped).
        book_meta:
            Metadata dict from YAML front matter.  May include ``pages``
            (int) and ``tags`` (list[str]).
        toc:
            TOC entry dicts as returned by :meth:`extract_toc_and_body`.

        Returns
        -------
        list[dict]
            Ordered list of ``{"text": str, "metadata": dict}`` chunks.
        """
        lines = text.splitlines()
        max_pages: Optional[int] = book_meta.get("pages")
        tags: list = book_meta.get("tags", [])

        # Partition TOC into chapter-level and section-level entries, then
        # build page-range objects for efficient page-based lookups
        chapter_toc, section_toc = MarkdownChunker._split_toc(toc)
        section_ranges = MarkdownChunker._build_toc_ranges(section_toc)
        chapter_ranges = MarkdownChunker._build_toc_ranges(chapter_toc)

        # ------------------------------------------------------------------
        # Pass 1: classify every line
        # ------------------------------------------------------------------
        classified: list[dict] = []
        # last_valid_page enforces strictly-increasing page numbers
        last_valid_page: int = -1
        # current_page provides page context to non-footer lines
        current_page: Optional[int] = None

        for raw_line in lines:
            # --- footer / page number? ---
            is_footer, page_num = MarkdownChunker._is_footer_line(
                raw_line, max_pages
            )
            if is_footer:
                if page_num is not None:
                    if page_num > last_valid_page:
                        # Valid advancing page — update context
                        last_valid_page = page_num
                        current_page = page_num
                        classified.append(
                            {"kind": "footer", "page": page_num, "raw": raw_line}
                        )
                    else:
                        # Page number went backwards — treat line as body text
                        classified.append(
                            {"kind": "body", "raw": raw_line, "page": current_page}
                        )
                else:
                    # Chapter footer line — no page number to extract
                    classified.append(
                        {"kind": "footer", "page": None, "raw": raw_line}
                    )
                continue

            # --- heading? ---
            heading = MarkdownChunker._classify_line(raw_line)
            if heading:
                kind_h, level, title = heading
                if kind_h == "drop_cap":
                    # Decorative initial — treat as body, not a real heading
                    classified.append(
                        {"kind": "body", "raw": raw_line, "page": current_page}
                    )
                    continue
                classified.append(
                    {
                        "kind": "heading",
                        "heading_kind": kind_h,
                        "level": level,
                        "title": title,
                        "raw": raw_line,
                        "page": current_page,
                    }
                )
                continue

            # Default: body text
            classified.append({"kind": "body", "raw": raw_line, "page": current_page})

        # ------------------------------------------------------------------
        # Pass 2: walk classified lines and emit chunks
        # ------------------------------------------------------------------
        # hierarchy maps heading level -> {title, chunk_index} so we can
        # reconstruct parent pointers and breadcrumb paths
        hierarchy: dict[int, dict] = {}
        chunks: list[dict] = []

        cur_title: Optional[str] = None
        cur_level: Optional[int] = None
        cur_page: Optional[int] = None
        running_page: Optional[int] = None  # last footer page seen
        cur_body_lines: list[str] = []

        def _parent_index() -> Optional[int]:
            """Return the chunk index of the nearest ancestor heading."""
            if cur_level is None:
                return None
            for lvl in sorted(hierarchy.keys(), reverse=True):
                if lvl < cur_level:
                    return hierarchy[lvl].get("chunk_index")
            return None

        def _hierarchy_titles() -> list[str]:
            """Return ancestor heading titles ordered root → parent."""
            return [
                hierarchy[lvl]["title"]
                for lvl in sorted(hierarchy.keys())
                if cur_level is None or lvl < cur_level
            ]

        def _flush() -> None:
            """Finalize the current chunk and append it to *chunks*."""
            nonlocal cur_title, cur_level, cur_page, cur_body_lines

            body = "\n".join(cur_body_lines).strip()
            cur_body_lines = []

            # Skip completely empty pre-heading content blocks
            if not body and cur_title is None:
                return

            # --- resolve toc_title and chapter ---
            # Prefer a title-based TOC match over a page-based one.  This
            # corrects the common off-by-one artefact where a heading is
            # physically printed on page N but the TOC lists page N+1.
            title_match_sec = MarkdownChunker._toc_entry_by_title(
                section_ranges, cur_title
            )
            title_match_chap = MarkdownChunker._toc_entry_by_title(
                chapter_ranges, cur_title
            )

            if title_match_sec is not None:
                # Direct section match — use the TOC's authoritative page
                sec_entry = title_match_sec
                toc_title = sec_entry.get("title")
                chapter = MarkdownChunker._chapter_for_page(
                    chapter_ranges, sec_entry.get("page", cur_page)
                )
            elif title_match_chap is not None:
                # The heading is itself a chapter title
                sec_entry = None
                toc_title = None
                chapter = title_match_chap.get("title")
            else:
                # No title match — fall back to page-based lookup
                sec_entry = MarkdownChunker._toc_entry_for_page(
                    section_ranges, cur_page
                )
                toc_title = sec_entry.get("title") if sec_entry else None
                chapter = MarkdownChunker._chapter_for_page(
                    chapter_ranges, cur_page
                )

            chunk_index = len(chunks)

            metadata = {
                "title": cur_title,
                "toc_title": toc_title,
                "chapter": chapter,
                "tags": tags,
                "page": cur_page,
                "tokens": _count_tokens(body),
                "parent_index": _parent_index(),
                "hierarchy": _hierarchy_titles(),
                # All book-level fields except tags (tags already at top level)
                "book": {k: v for k, v in book_meta.items() if k != "tags"},
                # Timing fields are stamped by process_markdown_file after
                # the full chunk list for this book is ready
                "chunking_started_at": None,
                "chunking_completed_at": None,
            }

            # Register this heading in the hierarchy and evict deeper levels
            # so that e.g. a new H2 invalidates any previously-seen H3/H4/…
            if cur_level is not None:
                hierarchy[cur_level] = {
                    "title": cur_title,
                    "chunk_index": chunk_index,
                }
                for lvl in list(hierarchy.keys()):
                    if lvl > cur_level:
                        del hierarchy[lvl]

            chunks.append({"text": body, "metadata": metadata})

            cur_title = None
            cur_level = None

        # Walk all classified lines and assemble chunks
        for item in classified:
            if item["kind"] == "footer":
                # Update running page context; do not add to body
                if item.get("page") is not None:
                    running_page = item["page"]
                continue

            if item["kind"] == "heading":
                _flush()  # close the previous section before opening a new one
                cur_title = item["title"]
                cur_level = item["level"]
                cur_page = running_page  # inherit the page at which this heading appears
                continue

            # Body line — accumulate for the current (or pre-heading) chunk
            cur_body_lines.append(item["raw"])

        _flush()  # finalize the last open chunk

        return chunks

    # ------------------------------------------------------------------
    # Private helpers — static methods so unit tests can call them directly
    # ------------------------------------------------------------------

    @staticmethod
    def _is_table_line(line: str) -> bool:
        """Return True if *line* looks like a Markdown table row (``|...|``)."""
        return bool(MarkdownChunker.TABLE_RE.match(line.strip()))

    @staticmethod
    def _is_prose_line(text: str) -> bool:
        """Return True if *text* looks like prose rather than a section title.

        Catches: sentences ending in punctuation, interior commas or
        semicolons that read like a list or clause, quoted dialogue, and
        hyphenated line-breaks.
        """
        t = text.strip()

        # Sentence-ending punctuation — hyphen also catches broken line wraps
        if MarkdownChunker.SENTENCE_END_RE.search(t):
            return True

        # Quote characters mid-line — almost certainly dialogue or prose
        if '"' in t or "\u201c" in t or "\u201d" in t:
            return True

        # Possessive or contraction — definitely prose
        if "'" in t or "\u2019" in t:
            return True

        # Interior comma or semicolon — reads as a list or clause, not a title.
        # (This rule is intentionally absent from _is_prose_line_strict because
        # italic titles from PDFs sometimes contain formatted numbers like 1,500.)
        if "," in t or ";" in t:
            return True

        return False

    @staticmethod
    def _is_prose_line_strict(text: str) -> bool:
        """Like :meth:`_is_prose_line` but without the comma/semicolon rule.

        Used for italic title candidates, which can contain commas in numbers
        (e.g. ``1,500 gold pieces``).  Compensates with a word-count guard:
        more than 6 words is almost certainly prose, not a title.
        """
        t = text.strip()
        if MarkdownChunker.SENTENCE_END_RE.search(t):
            return True
        if '"' in t or "\u201c" in t or "\u201d" in t:
            return True
        if "'" in t or "\u2019" in t:
            return True
        if len(t) > MarkdownChunker.MAX_TITLE_LEN:
            return True
        # PDF line-wrapping produces italic sentence fragments of 6+ words
        if len(t.split()) > 6:
            return True
        return False

    @staticmethod
    def _classify_line(line: str):
        """Classify *line* as a heading kind or return None.

        Only called for lines that are NOT already identified as footers.

        Returns
        -------
        tuple[str, int, str] | None
            ``(kind, level, title)`` where *kind* is one of
            ``'atx'``, ``'bold'``, ``'italic'``, or ``'drop_cap'``;
            *level* is 1–6 for ATX headers, 7 for bold, 8 for italic,
            and 0 for drop caps.  Returns ``None`` for ordinary body lines.
        """
        stripped = line.strip()

        if not stripped:
            return None
        # Table rows are always body
        if MarkdownChunker._is_table_line(stripped):
            return None
        # Code fences are always body
        if MarkdownChunker.CODE_FENCE_RE.match(stripped):
            return None

        # ATX headers always take priority over bold/italic heuristics
        m = MarkdownChunker.HEADER_RE.match(stripped)
        if m:
            title_raw = m.group(2).strip()
            # Strip inner bold/italic markers left behind by PDF converters
            title_clean = re.sub(r"\*\*(.+?)\*\*", r"\1", title_raw)
            title_clean = re.sub(r"_(.+?)_", r"\1", title_clean).strip()
            # A 1–2-character result is a decorative drop cap, not a heading
            if MarkdownChunker.DROP_CAP_RE.match(title_clean):
                return ("drop_cap", 0, title_clean)
            # ATX lines whose content looks like prose are rejected as headings
            if not MarkdownChunker._is_prose_line(title_clean):
                return ("atx", len(m.group(1)), title_clean)
            return None

        # Prose lead-in bold (**Bold.** rest of sentence) — always body text
        if MarkdownChunker.BOLD_LEADIN_RE.match(stripped):
            return None

        # Standalone bold: **Title**
        m = MarkdownChunker.BOLD_TITLE_RE.match(stripped)
        if m:
            title = m.group(1).strip()
            if MarkdownChunker.DROP_CAP_RE.match(title):
                return None
            if MarkdownChunker._is_prose_line(title):
                return None
            return ("bold", 7, title)

        # Standalone italic: _Title_
        m = MarkdownChunker.ITALIC_TITLE_RE.match(stripped)
        if m:
            title = m.group(1).strip()
            if MarkdownChunker.DROP_CAP_RE.match(title):
                return None
            if MarkdownChunker._is_prose_line_strict(title):
                return None
            return ("italic", 8, title)

        return None

    @staticmethod
    def _is_footer_line(
        line: str, max_pages: Optional[int]
    ) -> tuple[bool, Optional[int]]:
        """Detect footer lines and extract their page number.

        A footer is one of:

        * ``**12**`` — bold page number (common in PDF-extracted Markdown)
        * a bare integer on its own line, provided it is ≤ *max_pages*
        * a ``"Chapter N | …"`` chapter footer line

        Parameters
        ----------
        line:
            A single raw line from the document.
        max_pages:
            Upper bound on plausible page numbers.  ``None`` disables the
            check (all integers are accepted as page numbers).

        Returns
        -------
        tuple[bool, int | None]
            ``(is_footer, page_number_or_None)``
        """
        stripped = line.strip()

        m = MarkdownChunker.FOOTER_PAGE_RE.match(stripped)
        if m:
            page = int(m.group(1))
            if max_pages is None or page <= max_pages:
                return True, page

        m = MarkdownChunker.BARE_NUMBER_RE.match(stripped)
        if m:
            page = int(m.group(1))
            if max_pages is None or page <= max_pages:
                return True, page

        if MarkdownChunker.CHAPTER_FOOTER_RE.match(stripped):
            return True, None

        return False, None

    @staticmethod
    def _split_toc(toc: list) -> tuple[list, list]:
        """Partition TOC entries into chapter entries and section entries.

        *Chapter entries* — those whose title matches ``CHAPTER_RE`` — are
        used only to populate the ``chapter`` metadata field on each chunk.

        *Section entries* — everything else — drive ``toc_title`` assignment
        and page-range narrowing.

        This split prevents chapter TOC entries from polluting ``toc_title``
        when they share a page with the first section of that chapter.
        """
        chapters: list[dict] = []
        sections: list[dict] = []
        for entry in toc or []:
            if MarkdownChunker.CHAPTER_RE.search(entry.get("title", "")):
                chapters.append(entry)
            else:
                sections.append(entry)
        return chapters, sections

    @staticmethod
    def _build_toc_ranges(entries: list) -> list:
        """Augment TOC entries with ``end_page`` for range-based page lookups.

        ``end_page`` is set to (start page of the next entry with a different
        page) − 1.  Entries that share a page all receive the same
        ``end_page`` so none end up with ``end_page < page``.

        Parameters
        ----------
        entries:
            TOC entry dicts — order does not matter; they are sorted by page.

        Returns
        -------
        list[dict]
            A new list where every dict has the original fields plus
            ``end_page`` (int or ``None`` for the last entry).
        """
        if not entries:
            return []
        sorted_entries = sorted(entries, key=lambda e: e.get("page", 0))
        ranges = []
        for i, entry in enumerate(sorted_entries):
            start = entry.get("page", 0)
            end = None
            # Find the first subsequent entry that starts on a later page
            for j in range(i + 1, len(sorted_entries)):
                next_page = sorted_entries[j].get("page", start)
                if next_page > start:
                    end = next_page - 1
                    break
            ranges.append({**entry, "end_page": end})
        return ranges

    @staticmethod
    def _toc_entry_for_page(
        toc_ranges: list, page: Optional[int]
    ) -> Optional[dict]:
        """Return the best-matching TOC entry for a given page number.

        When multiple entries cover the same page, the entry with the highest
        ``page`` start (most specific match) is preferred; ties are broken by
        the entry's position in the sorted list (first wins).

        Parameters
        ----------
        toc_ranges:
            Output of :meth:`_build_toc_ranges`.
        page:
            Page number to look up.  Returns ``None`` when *page* is ``None``.
        """
        if page is None or not toc_ranges:
            return None
        best = None
        best_idx = None
        for idx, entry in enumerate(toc_ranges):
            start = entry.get("page", 0)
            end = entry.get("end_page")
            if start <= page and (end is None or page <= end):
                if best is None or start > best.get("page", 0):
                    best = entry
                    best_idx = idx
                elif start == best.get("page", 0) and idx < best_idx:
                    best = entry
                    best_idx = idx
        return best

    @staticmethod
    def _chapter_for_page(
        chapter_ranges: list, page: Optional[int]
    ) -> Optional[str]:
        """Return the chapter title that contains *page*, or ``None``."""
        entry = MarkdownChunker._toc_entry_for_page(chapter_ranges, page)
        return entry.get("title") if entry else None

    @staticmethod
    def _normalize(s: str) -> str:
        """Lower-case, collapse whitespace, and strip punctuation.

        Used for fuzzy title matching so that minor formatting differences
        between heading text and TOC entries do not prevent a match.
        """
        s = s.lower().strip()
        s = re.sub(r"[^\w\s]", "", s)
        return re.sub(r"\s+", " ", s)

    @staticmethod
    def _toc_entry_by_title(
        toc_ranges: list, title: Optional[str]
    ) -> Optional[dict]:
        """Find a TOC entry whose title fuzzy-matches *title*.

        Matching is case-insensitive and ignores punctuation and extra
        whitespace (via :meth:`_normalize`).

        Parameters
        ----------
        toc_ranges:
            Output of :meth:`_build_toc_ranges`.
        title:
            The heading text to search for.

        Returns
        -------
        dict | None
            The matching entry (with ``end_page``), or ``None``.
        """
        if not title or not toc_ranges:
            return None
        needle = MarkdownChunker._normalize(title)
        for entry in toc_ranges:
            if MarkdownChunker._normalize(entry.get("title", "")) == needle:
                return entry
        return None


# ---------------------------------------------------------------------------
# Vector store — write_chunked_markdown
# ---------------------------------------------------------------------------


def write_chunked_markdown(
    path: "Path | str",
    chunks: list[dict],
    book_meta: dict,
) -> None:
    """Embed *chunks* and write them to Qdrant or LanceDB.

    Qdrant is used when ``QDRANT_HOST`` is TCP-reachable; otherwise the
    function falls back to a local LanceDB database at ``LANCEDB_PATH``.

    All previously stored chunks whose ``source_file`` matches *path* are
    deleted before the new batch is written, so a re-processed file never
    leaves stale vectors behind.

    Parameters
    ----------
    path:
        Path to the source Markdown file.  Stored as ``source_file`` in the
        vector store so previous entries can be deleted by filter.
    chunks:
        Chunk dicts as returned (and timing-stamped) by
        :func:`process_markdown_file`.
    book_meta:
        Front-matter metadata for the book — kept for future use (e.g.
        per-book collection routing).
    """
    if not chunks:
        logger.warning(
            "Chunking pipeline: no chunks to write for %s — skipping.", path
        )
        return

    source_key = str(path)
    embedder = _get_embedder()

    # Embed all chunk texts in a single batch call — much faster than one-by-one
    texts = [c.get("text", "") for c in chunks]
    vectors = embedder.encode(texts, show_progress_bar=False).tolist()

    if _qdrant_reachable():
        _write_to_qdrant(source_key, chunks, vectors)
    else:
        logger.info(
            "Chunking pipeline: Qdrant not reachable at %s:%d — using LanceDB.",
            QDRANT_HOST,
            QDRANT_PORT,
        )
        _write_to_lancedb(source_key, chunks, vectors)


def _write_to_qdrant(
    source_key: str,
    chunks: list[dict],
    vectors: list[list[float]],
) -> None:
    """Delete old points for *source_key* and upsert new ones to Qdrant.

    Creates the collection with cosine-distance EMBEDDING_DIM vectors if it
    does not yet exist.
    """
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels

    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # Create the collection on first use
    existing = {c.name for c in client.get_collections().collections}
    if QDRANT_COLLECTION not in existing:
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=qmodels.VectorParams(
                size=EMBEDDING_DIM,
                distance=qmodels.Distance.COSINE,
            ),
        )
        logger.info(
            "Chunking pipeline: created Qdrant collection '%s'.",
            QDRANT_COLLECTION,
        )

    # Delete all existing points for this source file so we start clean
    client.delete(
        collection_name=QDRANT_COLLECTION,
        points_selector=qmodels.FilterSelector(
            filter=qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="source_file",
                        match=qmodels.MatchValue(value=source_key),
                    )
                ]
            )
        ),
    )
    logger.info(
        "Chunking pipeline: deleted existing Qdrant points for '%s'.",
        source_key,
    )

    # Build PointStruct objects — each point carries the full metadata as payload
    points = []
    for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
        payload = {"source_file": source_key, **chunk["metadata"]}
        points.append(
            qmodels.PointStruct(
                id=_deterministic_uuid(source_key, idx),
                vector=vector,
                payload=payload,
            )
        )

    client.upsert(collection_name=QDRANT_COLLECTION, points=points)
    logger.info(
        "Chunking pipeline: upserted %d points to Qdrant collection '%s'.",
        len(points),
        QDRANT_COLLECTION,
    )


def _write_to_lancedb(
    source_key: str,
    chunks: list[dict],
    vectors: list[list[float]],
) -> None:
    """Delete old rows for *source_key* and append new rows to LanceDB.

    Nested metadata fields (``book``, ``tags``, ``hierarchy``) are
    JSON-serialised to strings because LanceDB requires a flat, consistent
    schema when appending to an existing table.
    """
    import lancedb

    db = lancedb.connect(LANCEDB_PATH)

    # Build flat row dicts compatible with LanceDB's Arrow-backed storage
    rows = []
    for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
        meta = chunk.get("metadata", {})
        rows.append(
            {
                "id": _deterministic_uuid(source_key, idx),
                "source_file": source_key,
                "text": chunk.get("text", ""),
                "vector": vector,
                "title": meta.get("title"),
                "toc_title": meta.get("toc_title"),
                "chapter": meta.get("chapter"),
                # Nested objects serialised to JSON strings
                "tags": _safe_json(meta.get("tags", [])),
                "page": meta.get("page"),
                "tokens": meta.get("tokens", 0),
                "parent_index": meta.get("parent_index"),
                "hierarchy": _safe_json(meta.get("hierarchy", [])),
                "book": _safe_json(meta.get("book", {})),
                "chunking_started_at": meta.get("chunking_started_at"),
                "chunking_completed_at": meta.get("chunking_completed_at"),
            }
        )

    if LANCEDB_TABLE in db.table_names():
        tbl = db.open_table(LANCEDB_TABLE)
        # Escape single quotes in the source key for the SQL predicate
        escaped = source_key.replace("'", "''")
        tbl.delete(f"source_file = '{escaped}'")
        logger.info(
            "Chunking pipeline: deleted existing LanceDB rows for '%s'.",
            source_key,
        )
        tbl.add(rows)
    else:
        db.create_table(LANCEDB_TABLE, data=rows)
        logger.info(
            "Chunking pipeline: created LanceDB table '%s'.", LANCEDB_TABLE
        )

    logger.info(
        "Chunking pipeline: wrote %d rows to LanceDB table '%s'.",
        len(rows),
        LANCEDB_TABLE,
    )


# ---------------------------------------------------------------------------
# Per-file orchestration
# ---------------------------------------------------------------------------


async def process_markdown_file(path: "Path | str") -> tuple[list, list]:
    """Parse, chunk, embed and store one Markdown file end-to-end.

    Steps:

    1. Read the file and parse its YAML front matter.
    2. Detect and strip the TOC; keep the section list for metadata.
    3. Chunk the remaining body into semantic sections.
    4. Stamp each chunk's metadata with wall-clock timing for this book.
    5. Write all chunks to the vector store in one batch.
    6. Log a structured summary; emit an error if the result looks sparse.

    The CPU-bound chunking and I/O-bound write steps are run in the default
    thread executor so the event loop stays responsive during processing.

    Parameters
    ----------
    path:
        Path to the ``.md`` source file.

    Returns
    -------
    tuple[list[dict], list[dict]]
        ``(chunks, toc)`` — the produced chunks and the parsed TOC entries.
    """
    path = Path(path)
    logger.info("Chunking pipeline: starting  %s", path.name)

    text = path.read_text(encoding="utf-8", errors="ignore")

    # 1. Parse YAML front matter
    book_meta, body = MarkdownChunker.parse_frontmatter(text)

    # 2. Extract TOC (strips it from body so it is not chunked as prose)
    toc, body = MarkdownChunker.extract_toc_and_body(body)

    # Record wall-clock start time before the CPU-bound chunking pass
    started_at = datetime.now(timezone.utc).isoformat()

    # 3. Chunk — run in executor to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    chunks = await loop.run_in_executor(
        None, MarkdownChunker.chunk_markdown, body, book_meta, toc
    )

    completed_at = datetime.now(timezone.utc).isoformat()

    # 4. Stamp every chunk with the same timing values for this book pass
    for chunk in chunks:
        chunk["metadata"]["chunking_started_at"] = started_at
        chunk["metadata"]["chunking_completed_at"] = completed_at

    # Derive summary stats for the quality gate and log line
    stats = {
        "total_chunks": len(chunks),
        "empty_chunks": sum(1 for c in chunks if not c.get("text")),
        "total_tokens": sum(c["metadata"].get("tokens", 0) for c in chunks),
    }

    # 5. Write to vector store — also run in executor (network / disk I/O)
    await loop.run_in_executor(
        None, write_chunked_markdown, path, chunks, book_meta
    )

    logger.info(
        "Chunking pipeline: finished  %s — %d chunks, %d tokens, "
        "started=%s  completed=%s",
        path.name,
        stats["total_chunks"],
        stats["total_tokens"],
        started_at,
        completed_at,
    )

    # Quality gate — warn when the result looks too sparse to be useful
    if not _chunking_ok(stats):
        logger.error(
            "Chunking pipeline: %s — chunking likely insufficient "
            "(total_chunks=%d, empty_chunks=%d). "
            "Fallback strategy recommended.",
            path.name,
            stats["total_chunks"],
            stats["empty_chunks"],
        )

    return chunks, toc


# ---------------------------------------------------------------------------
# Background pipeline loop
# ---------------------------------------------------------------------------


async def run_chunking_pipeline() -> None:
    """Background loop: scan Markdown files, chunk changed ones, sleep, repeat.

    Mirrors the structure of ``run_pdf_pipeline``.  On each iteration, every
    ``.md`` file under ``LIBRARY_DIR`` is checked: if the file's mtime is
    newer than the ``chunking_completed_at`` stored in Redis (or no entry
    exists yet), the file is queued for (re-)chunking.

    State keys stored in Redis under ``memory.chunking_pipeline_state``
    per file path:

    * ``status``               — one of the STATUS_* constants
    * ``chunking_completed_at`` — ISO-format UTC timestamp of the last
      successful chunk write; used for the mtime comparison
    * ``lastChunkingStart``    — ISO timestamp when the last run began
    * ``lastChunkingComplete`` — ISO timestamp when the last run ended
    """
    logger.info(
        "Chunking pipeline started. Watching: %s  (interval: %ss)",
        LIBRARY_DIR,
        CHUNK_CHECK_INTERVAL_SECONDS,
    )

    while True:
        if not LIBRARY_DIR.exists():
            logger.debug(
                "Chunking pipeline: library dir not found, skipping check."
            )
            await asyncio.sleep(CHUNK_CHECK_INTERVAL_SECONDS)
            continue

        md_files = sorted(
            p for p in LIBRARY_DIR.rglob("*.md")
            if not any(part.startswith(".") for part in p.parts[len(LIBRARY_DIR.parts):])
        )
        logger.debug(
            "Chunking pipeline: check running, %d Markdown file(s) found.",
            len(md_files),
        )

        # ── Phase 1: compare mtime to last chunking_completed_at ────────────
        queued_paths: list[Path] = []

        for md_path in md_files:
            md_key = str(md_path)
            file_mtime = md_path.stat().st_mtime

            with Memory() as memory:
                if not hasattr(memory, "chunking_pipeline_state"):
                    memory.chunking_pipeline_state = {}
                entry = memory.chunking_pipeline_state.get(md_key) or {}
                # Mark Checking so the status dashboard reflects activity
                memory.chunking_pipeline_state[md_key] = {
                    **entry,
                    "status": STATUS_CHECKING,
                }

            completed_at_str = entry.get("chunking_completed_at")
            if completed_at_str:
                try:
                    completed_ts = datetime.fromisoformat(
                        completed_at_str
                    ).timestamp()
                    needs_processing = file_mtime > completed_ts
                    reason = (
                        "file modified after last chunk"
                        if needs_processing
                        else None
                    )
                except ValueError:
                    # Stored timestamp is malformed — reprocess to be safe
                    needs_processing = True
                    reason = "invalid stored timestamp"
            else:
                # No record at all — file has never been chunked
                needs_processing = True
                reason = "never chunked"

            if needs_processing:
                with Memory() as memory:
                    if not hasattr(memory, "chunking_pipeline_state"):
                        memory.chunking_pipeline_state = {}
                    entry = memory.chunking_pipeline_state.get(md_key) or {}
                    memory.chunking_pipeline_state[md_key] = {
                        **entry,
                        "status": STATUS_QUEUED,
                    }
                queued_paths.append(md_path)
                logger.info(
                    "Chunking pipeline: %s queued — %s.", md_path.name, reason
                )
            else:
                with Memory() as memory:
                    if not hasattr(memory, "chunking_pipeline_state"):
                        memory.chunking_pipeline_state = {}
                    entry = memory.chunking_pipeline_state.get(md_key) or {}
                    memory.chunking_pipeline_state[md_key] = {
                        **entry,
                        "status": STATUS_CHUNKED,
                    }

        # ── Phase 2: process each queued file ───────────────────────────────
        for md_path in queued_paths:
            md_key = str(md_path)
            start_dt = datetime.now(timezone.utc)
            started_at = start_dt.isoformat()

            with Memory() as memory:
                if not hasattr(memory, "chunking_pipeline_state"):
                    memory.chunking_pipeline_state = {}
                entry = memory.chunking_pipeline_state.get(md_key) or {}
                memory.chunking_pipeline_state[md_key] = {
                    **entry,
                    "status": STATUS_CHUNKING,
                    "lastChunkingStart": started_at,
                }

            logger.info(
                "Chunking pipeline: processing %s — started at %s",
                md_path.name,
                started_at,
            )

            try:
                chunks, toc = await process_markdown_file(md_path)
            except Exception as e:
                logger.error(
                    "Chunking pipeline: failed to process %s — %s: %s",
                    md_path.name,
                    type(e).__name__,
                    e,
                )
                continue

            end_dt = datetime.now(timezone.utc)
            completed_at = end_dt.isoformat()
            elapsed = (end_dt - start_dt).total_seconds()

            with Memory() as memory:
                if not hasattr(memory, "chunking_pipeline_state"):
                    memory.chunking_pipeline_state = {}
                entry = memory.chunking_pipeline_state.get(md_key) or {}
                memory.chunking_pipeline_state[md_key] = {
                    **entry,
                    "status": STATUS_CHUNKED,
                    # Stored for the mtime comparison on the next iteration
                    "chunking_completed_at": completed_at,
                    "lastChunkingComplete": completed_at,
                }

            logger.info(
                "Chunking pipeline: %s — completed at %s "
                "(elapsed: %.1fs, %d chunks)",
                md_path.name,
                completed_at,
                elapsed,
                len(chunks),
            )

        await asyncio.sleep(CHUNK_CHECK_INTERVAL_SECONDS)
