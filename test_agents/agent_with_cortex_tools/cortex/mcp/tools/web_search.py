import logging

import httpx

logger = logging.getLogger(__name__)


def web_search(query: str = "latest AI news", max_results: int = 5) -> str:
    """Search the web using DuckDuckGo and return a summary of the top results.

    Uses the DuckDuckGo Instant Answer API. Returns an abstract and related
    topics when available; falls back to a short error message if the network
    is unreachable.

    Args:
        query: The search query string to look up on the web.
        max_results: Maximum number of related topics to include in the response.
    """
    try:
        response = httpx.get(
            "https://api.duckduckgo.com/",
            params={
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1",
            },
            timeout=10.0,
            follow_redirects=True,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        logger.error("web_search: request failed: %s", exc)
        return f"Web search unavailable: {exc}"

    parts = []

    abstract = data.get("AbstractText", "")
    if abstract:
        source = data.get("AbstractSource", "")
        url = data.get("AbstractURL", "")
        header = f"Summary ({source}):" if source else "Summary:"
        parts.append(f"{header}\n{abstract}\n{url}".strip())

    for item in data.get("RelatedTopics", [])[:max_results]:
        if isinstance(item, dict) and "Text" in item and "FirstURL" in item:
            parts.append(f"- {item['Text']}\n  {item['FirstURL']}")

    if not parts:
        return f"No results found for: {query!r}"

    return "\n\n".join(parts[:max_results])
