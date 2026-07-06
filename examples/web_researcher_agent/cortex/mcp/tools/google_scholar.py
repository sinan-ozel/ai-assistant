import logging
import os

import httpx

logger = logging.getLogger(__name__)

_SERPER_URL = "https://google.serper.dev/scholar"


@tool.mcp(title="Google Scholar Search", read_only_hint=True, open_world_hint=True)
def google_scholar_search(
    query: str = "transformer neural networks",
    max_results: int = 5,
) -> str:
    """Search Google Scholar for academic papers matching the query.

    Returns paper titles, publication info, citation counts, and abstracts.
    Requires the SERPER_API_KEY environment variable.

    Args:
        query: The academic search query, e.g. a research topic or paper title.
        max_results: Maximum number of papers to return.
    """
    api_key = os.environ.get("SERPER_API_KEY", "")
    if not api_key:
        logger.error("google_scholar_search: SERPER_API_KEY is not set")
        return "Google Scholar search is unavailable: SERPER_API_KEY is not configured."

    try:
        response = httpx.post(
            _SERPER_URL,
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "num": max_results},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        logger.error("google_scholar_search: request failed: %s", exc)
        return f"Google Scholar search unavailable: {exc}"

    papers = data.get("organic", [])
    if not papers:
        return f"No papers found for: {query!r}"

    parts = []
    for i, paper in enumerate(papers[:max_results], 1):
        lines = [f"[{i}] {paper.get('title', 'Untitled')}"]
        pub_info = paper.get("publicationInfo", "")
        if pub_info:
            lines.append(f"  Published: {pub_info}")
        cited = paper.get("citedBy")
        if cited is not None:
            lines.append(f"  Cited by: {cited}")
        snippet = paper.get("snippet", "")
        if snippet:
            lines.append(f"  {snippet}")
        link = paper.get("link", "")
        if link:
            lines.append(f"  {link}")
        parts.append("\n".join(lines))

    return "\n\n".join(parts)
