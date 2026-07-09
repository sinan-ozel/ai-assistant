"""Library search with a canonical-tag ladder.

Named ``search.py`` on purpose: the functions register as
``search__library_search`` / ``search__library_search_full`` and the first
shadows the framework's default library tool, so the model sees exactly the
two library searches defined here.

``library_search`` walks the canonical collections in priority order
(``LIBRARY_TAGS_PRIMARY``, then ``LIBRARY_TAGS_FALLBACK``) and stops at the
first tag with a strong match.  ``library_search_full`` covers the rest of
the library — everything whose tags are NOT in the canonical lists.

Both call the agent's own /private/v1/search REST endpoint (the MCP server
runs in the same container) instead of importing framework internals, so
swapping the local library for a graph-retrieval service later means editing
only this file.

Tags are the folder names under ``cortex/library/`` (one tag per folder
level), so the canonical tags require the books to live in folders named
after them, e.g. ``cortex/library/eberron_5e24_kanon/…``.  Tag filtering
matches any level of nesting.
"""

import logging
import os

import httpx

logger = logging.getLogger(__name__)

_SEARCH_URL = "http://localhost:8000/private/v1/search"

# Cosine-equivalent score above which a passage counts as a strong match.
_STRONG_SCORE = float(os.environ.get("LIBRARY_STRONG_MATCH_SCORE", "0.5"))


def _tags_from_env(var: str, default: str) -> list:
    return [t.strip() for t in os.environ.get(var, default).split(",") if t.strip()]


# Canonical collections, searched in priority order.
_PRIMARY_TAGS = _tags_from_env(
    "LIBRARY_TAGS_PRIMARY",
    "eberron_5e24_kanon,eberron_5e_kanon,eberron_5e_canon,my_eberron",
)
# Consulted only when no primary tag has a strong match.
_FALLBACK_TAGS = _tags_from_env("LIBRARY_TAGS_FALLBACK", "eberron_3e")


def _citation(result: dict) -> str:
    """Return a '(Book Title, p. N)' citation string for a search result."""
    book = result.get("book") or {}
    title = book.get("title") or book.get("title_from_pdf")
    if not title:
        file_path = result.get("file_path", "")
        title = os.path.splitext(os.path.basename(file_path))[0] or "Unknown"
    page = result.get("page_number")
    if page is not None and page > 0:
        return f"({title}, p. {page})"
    return f"({title}, page unknown)"


def _search(query: str, top_k: int, filter_payload: dict = None) -> list:
    """POST /private/v1/search; raises on transport/HTTP errors."""
    body = {"query": query, "top_k": top_k, "stream": False}
    if filter_payload:
        body["filter"] = filter_payload
    response = httpx.post(_SEARCH_URL, json=body, timeout=30.0)
    response.raise_for_status()
    return response.json()


def _format_results(results: list, tag_of: dict) -> str:
    parts = []
    for i, result in enumerate(results, 1):
        score = float(result.get("score", 0.0))
        label = "STRONG" if score >= _STRONG_SCORE else "weak"
        tag = tag_of.get(id(result), "")
        header = f"[{i}] {_citation(result)} — {label} match, score {score:.2f}"
        if tag:
            header += f", collection: {tag}"
        lines = [header]
        book = result.get("book") or {}
        author = book.get("author_from_pdf") or ""
        if author:
            lines.append(f"  Author: {author}")
        chapter = result.get("chapter_label_in_toc") or ""
        if chapter:
            lines.append(f"  Chapter: {chapter}")
        section = result.get("section_title") or ""
        if section:
            lines.append(f"  Section: {section}")
        text = result.get("text", "")
        if text:
            lines.append(f"  {text}")
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


@tool.mcp(title="Canonical Library Search", read_only_hint=True)
def library_search(query: str = "the Blood of Vol", top_k: int = 5) -> str:
    """Search the canonical Eberron collections of the DM's library.

    Walks the canonical collections in priority order (5e 2024 kanon, 5e
    kanon, 5e canon, this campaign's own material, then 3e) and stops at the
    first collection with a strong match. Results carry the book title and
    page number required for citations.

    Args:
        query: Free-text lore query — a name, faction, place, or theme.
        top_k: Maximum number of passages to return per collection.
    """
    collected: list = []
    tag_of: dict = {}
    strong_tag = None
    try:
        for tag in _PRIMARY_TAGS + _FALLBACK_TAGS:
            if strong_tag is None and tag in _FALLBACK_TAGS:
                logger.info(
                    "library_search: no strong match in primary tags %s — "
                    "extending to fallback tag %r.",
                    _PRIMARY_TAGS,
                    tag,
                )
            results = _search(query, top_k, {"book.tags": tag})
            for r in results:
                tag_of[id(r)] = tag
            collected.extend(results)
            if any(float(r.get("score", 0.0)) >= _STRONG_SCORE for r in results):
                strong_tag = tag
                break
    except Exception as exc:
        logger.error("library_search: request failed: %s", exc)
        return (
            f"Canonical library search unavailable: {exc}. "
            "Note this in your answer and escalate to the next stage."
        )

    if not collected:
        return (
            f"No results in the canonical collections "
            f"({', '.join(_PRIMARY_TAGS + _FALLBACK_TAGS)}) for: {query!r}. "
            "If rephrasing the query does not help either, reply with the "
            "escalation marker so the search can extend to the rest of the "
            "library and Keith Baker's blog."
        )

    body = _format_results(collected, tag_of)
    if strong_tag is not None:
        footer = (
            f"SOURCE: CANONICAL LIBRARY, strong match in collection "
            f"'{strong_tag}'. Answer from these passages and cite each as "
            "(Book Title, p. N). Do not escalate."
        )
    else:
        footer = (
            "SOURCE: CANONICAL LIBRARY, but no strong matches in any "
            "canonical collection. If these passages do not actually answer "
            "the request, reply with the escalation marker; if they do, "
            "answer and cite each as (Book Title, p. N)."
        )
    return body + "\n\n" + footer


@tool.mcp(title="Full Library Search", read_only_hint=True)
def library_search_full(query: str = "the Blood of Vol", top_k: int = 5) -> str:
    """Search the rest of the DM's library — everything OUTSIDE the
    canonical Eberron collections, which were already searched.

    Results carry the book title and page number required for citations.

    Args:
        query: Free-text lore query — a name, faction, place, or theme.
        top_k: Maximum number of passages to return.
    """
    canonical = set(_PRIMARY_TAGS + _FALLBACK_TAGS)
    try:
        # The endpoint's filter is equality-only, so exclusion happens here:
        # over-fetch, then drop books tagged with a canonical collection.
        results = _search(query, top_k * 3)
    except Exception as exc:
        logger.error("library_search_full: request failed: %s", exc)
        return (
            f"Library search unavailable: {exc}. "
            "Note this in your answer and continue with search_keith_baker."
        )

    rest = [
        r
        for r in results
        if not canonical.intersection((r.get("book") or {}).get("tags") or [])
    ][:top_k]

    if not rest:
        return (
            f"No results in the rest of the library for: {query!r} (the "
            "canonical collections were already searched in the previous "
            "stage). Try search_keith_baker next."
        )

    any_strong = any(
        float(r.get("score", 0.0)) >= _STRONG_SCORE for r in rest
    )
    body = _format_results(rest, {})
    if any_strong:
        footer = (
            "SOURCE: LOCAL LIBRARY (non-canonical shelves). Strong matches "
            "found — answer from these passages and cite each as "
            "(Book Title, p. N)."
        )
    else:
        footer = (
            "SOURCE: LOCAL LIBRARY (non-canonical shelves), no strong "
            "matches. You may still use these passages (cite book + page), "
            "and also try search_keith_baker."
        )
    return body + "\n\n" + footer
