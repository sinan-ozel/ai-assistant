"""Default library-search MCP tool backed by Qdrant (or LanceDB fallback).

Delegates to the shared ``common.search.run_search`` function so the same
query path — embedding, backend selection, collection resolution, scoring —
is exercised whether the call comes from the MCP tool or the REST endpoint.

Each result includes the full provenance extracted by the ingestion pipelines:

  From the PDF front matter (set by pdf_pipeline.py):
    book.title            — unique top-level heading (body_title in front matter)
    book.title_from_pdf   — title from the PDF document metadata
    book.author_from_pdf  — author from the PDF document metadata
    book.page_count_from_pdf  — total pages in the PDF
    book.tags             — path components under cortex/library/ (one per folder level)

  From the Markdown chunker (set by chunking_pipeline.py):
    section_title         — ATX / bold / italic heading of this chunk's section
    section_title_in_toc  — matching Table-of-Contents entry title (if found)
    chapter_label_in_toc  — TOC chapter label that contains this section
    section_hierarchy     — ordered list of ancestor section titles (root → parent)
    page_number           — page on which this section starts (−1 when unknown)
    file_path             — library-relative path, e.g. "shelf2/mybook.pdf"
"""

import logging
import socket

from common.search import QDRANT_HOST, QDRANT_PORT, run_search

logger = logging.getLogger(__name__)


def _qdrant_reachable() -> bool:
    try:
        with socket.create_connection((QDRANT_HOST, QDRANT_PORT), timeout=2.0):
            return True
    except OSError:
        return False


def _log_qdrant_unavailable(context: str) -> None:
    logger.error(
        "library_search: Qdrant is not reachable — %s.\n"
        "  Attempted connection: %s:%d\n"
        "  Environment variables (current values):\n"
        "    QDRANT_HOST = '%s'  (default: 'qdrant')\n"
        "    QDRANT_PORT = '%d'  (default: 6333)\n"
        "  To fix:\n"
        "    1. Start a Qdrant instance, e.g.:\n"
        "         docker run -p 6333:6333 qdrant/qdrant\n"
        "    2. Ensure QDRANT_HOST and QDRANT_PORT in your docker-compose or\n"
        "       environment point to that instance.\n"
        "    3. Place documents under cortex/library/ so the chunking pipeline\n"
        "       indexes them into Qdrant on startup.\n"
        "  Without Qdrant, run_search falls back to LanceDB at LANCEDB_PATH,\n"
        "  which is empty unless documents were previously indexed locally.",
        context,
        QDRANT_HOST,
        QDRANT_PORT,
        QDRANT_HOST,
        QDRANT_PORT,
    )


@tool.mcp(title="Library Search", read_only_hint=True)
def library_search(
    query: str = "what is Eberron?",
    collection: str = "",
    top_k: int = 5,
    book: dict = {"tags": "", "title_from_pdf": "", "author_from_pdf": ""},
) -> str:
    """Search the library vector database for document chunks relevant to a query.

    Returns ranked chunks with full provenance: book title, author, tags,
    chapter, section heading, breadcrumb path, and page number. Use this
    context to cite sources accurately when answering.

    Args:
        query: The natural-language search query used to find relevant documents.
        collection: Qdrant collection name to search. Leave empty to search all collections. Collections correspond to top-level subfolders under cortex/library/.
        top_k: Maximum number of document chunks to return.
        book: Filter by book-level metadata. Supported keys: tags (library subfolder label, e.g. "shelf2"), title_from_pdf (exact PDF title), author_from_pdf (exact PDF author). Set a key to an empty string to skip that filter.
    """
    filter_payload = {f"book.{k}": v for k, v in book.items() if v} or None
    collections = [collection] if collection else None

    try:
        results = run_search(
            query=query,
            collections=collections,
            top_k=top_k,
            filter_payload=filter_payload,
        )
    except Exception as exc:
        if not _qdrant_reachable():
            _log_qdrant_unavailable(f"run_search raised {type(exc).__name__}: {exc}")
        else:
            logger.error(
                "library_search: run_search failed: %s", exc, exc_info=True
            )
        return "Library search is unavailable."

    _result_lines = []
    for _i, _hit in enumerate(results, start=1):
        _book_meta = _hit.get("book") or {}
        _book_title = (
            _book_meta.get("title")
            or _book_meta.get("title_from_pdf")
            or ""
        )
        _file = _hit.get("file_path") or _hit.get("collection") or "?"
        _section = _hit.get("section_title") or ""
        _score = _hit.get("score", 0.0)
        _line = f"  [{_i}] score={_score:.3f}  {_file}"
        if _book_title:
            _line += f"  book={_book_title!r}"
        if _section:
            _line += f"  § {_section!r}"
        _result_lines.append(_line)

    logger.debug(
        "library_search: query=%r  top_k=%d  →  %d chunk(s) returned\n%s",
        query,
        top_k,
        len(results),
        "\n".join(_result_lines) if _result_lines else "  (none)",
    )

    if not results:
        if not _qdrant_reachable():
            _log_qdrant_unavailable("run_search returned no results")
        return "No relevant documents found."

    parts = []
    for i, hit in enumerate(results, start=1):
        text = hit.get("text") or ""
        score = hit.get("score", 0.0)

        book_meta = hit.get("book") or {}
        book_title = book_meta.get("title") or book_meta.get("title_from_pdf") or ""
        author = book_meta.get("author_from_pdf") or ""
        tags: list = book_meta.get("tags") or []

        section_title = hit.get("section_title") or ""
        chapter = hit.get("chapter_label_in_toc") or ""
        page_num = hit.get("page_number")
        hierarchy: list = hit.get("section_hierarchy") or []
        file_path = hit.get("file_path") or hit.get("collection") or ""

        lines = [f"[{i}] score={score:.3f}"]
        if file_path:
            lines.append(f"  source:    {file_path}")
        if book_title:
            lines.append(f"  book:      {book_title}")
        if author:
            lines.append(f"  author:    {author}")
        if tags:
            lines.append(f"  tags:      {', '.join(str(t) for t in tags)}")
        if chapter:
            lines.append(f"  chapter:   {chapter}")
        if len(hierarchy) > 1:
            lines.append(f"  path:      {' > '.join(hierarchy[:-1])}")
        if section_title:
            lines.append(f"  section:   {section_title}")
        if page_num is not None and page_num > 0:
            lines.append(f"  page:      {page_num}")
        lines.append("")
        lines.append(text)

        parts.append("\n".join(lines))

    return "\n\n---\n\n".join(parts)


