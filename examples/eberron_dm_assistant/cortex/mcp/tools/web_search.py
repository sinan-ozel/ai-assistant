import logging
import os

import httpx

logger = logging.getLogger(__name__)

_SERPAPI_URL = "https://serpapi.com/search.json"


def _serpapi_search(query: str, max_results: int) -> list | str:
    """Run a SerpApi Google search; return organic results or an error string."""
    api_key = os.environ.get("SERPAPI_API_KEY", "")
    if not api_key:
        logger.error("web_search: SERPAPI_API_KEY is not set")
        return "Web search is unavailable: SERPAPI_API_KEY is not configured."

    try:
        response = httpx.get(
            _SERPAPI_URL,
            params={
                "engine": "google",
                "q": query,
                "num": max_results,
                "api_key": api_key,
            },
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        logger.error("web_search: request failed: %s", exc)
        return f"Web search unavailable: {exc}"

    return data.get("organic_results", [])


def _format_results(results: list, max_results: int, source_note: str) -> str:
    parts = []
    for i, hit in enumerate(results[:max_results], 1):
        lines = [f"[{i}] {hit.get('title', 'Untitled')}"]
        snippet = hit.get("snippet", "")
        if snippet:
            lines.append(f"  {snippet}")
        link = hit.get("link", "")
        if link:
            lines.append(f"  {link}")
        parts.append("\n".join(lines))
    return "\n\n".join(parts) + "\n\n" + source_note


@tool.mcp(title="Search Keith Baker's Site", read_only_hint=True, open_world_hint=True)
def search_keith_baker(query: str = "Lady Illmarrow", max_results: int = 5) -> str:
    """Search keith-baker.com, the Eberron creator's own site (kanon).

    Use this AFTER library_search comes back weak or empty. Keith Baker's
    word is authoritative but not official published canon.

    Args:
        query: Lore query — a name, faction, place, or theme.
        max_results: Maximum number of results to return.
    """
    results = _serpapi_search(f"site:keith-baker.com {query}", max_results)
    if isinstance(results, str):
        return results
    if not results:
        return (
            f"Nothing on keith-baker.com for: {query!r}. "
            "Try search_eberron_reddit next."
        )
    return _format_results(
        results,
        max_results,
        "SOURCE: KEITH BAKER'S SITE (kanon — the setting creator's word, "
        "not official published canon). Cite as "
        "(Keith Baker, kanon — <url>). Use read_web_page on a promising "
        "link if the snippet is not enough.",
    )


@tool.mcp(title="Search the Eberron Subreddit", read_only_hint=True, open_world_hint=True)
def search_eberron_reddit(query: str = "Lady Illmarrow minions", max_results: int = 5) -> str:
    """Search reddit.com/r/Eberron — community discussion of the setting.

    Use this after Keith Baker's site. Discussion may point at canon
    sources, but Reddit itself is NOT a canon source.

    Args:
        query: Lore query — a name, faction, place, or theme.
        max_results: Maximum number of results to return.
    """
    results = _serpapi_search(f"site:reddit.com/r/Eberron {query}", max_results)
    if isinstance(results, str):
        return results
    if not results:
        return (
            f"Nothing on r/Eberron for: {query!r}. "
            "Try search_eberron_wiki or search_world_anvil next."
        )
    return _format_results(
        results,
        max_results,
        "SOURCE: r/EBERRON (community discussion — NOT canon). Anything "
        "used from here must be labelled as not canon, with a link. If a "
        "post cites a book, prefer confirming via library_search.",
    )


@tool.mcp(title="Search the Eberron Wiki", read_only_hint=True, open_world_hint=True)
def search_eberron_wiki(query: str = "Lady Illmarrow", max_results: int = 5) -> str:
    """Search eberron.fandom.com, the fan-maintained Eberron wiki.

    Last resort along with search_world_anvil. Fan-maintained: NOT canon.

    Args:
        query: Lore query — a name, faction, place, or theme.
        max_results: Maximum number of results to return.
    """
    results = _serpapi_search(f"site:eberron.fandom.com {query}", max_results)
    if isinstance(results, str):
        return results
    if not results:
        return f"Nothing on the Eberron wiki for: {query!r}."
    return _format_results(
        results,
        max_results,
        "SOURCE: EBERRON FANDOM WIKI (fan-maintained — NOT canon). "
        "Anything used from here must be clearly labelled as not canon, "
        "with a link.",
    )


@tool.mcp(title="Search World Anvil Eberron Worlds", read_only_hint=True, open_world_hint=True)
def search_world_anvil(query: str = "undead villain", max_results: int = 5) -> str:
    """Search worldanvil.com for Eberron campaign worlds and articles.

    Last resort along with search_eberron_wiki. These are other DMs' fan
    creations: NOT canon.

    Args:
        query: Lore query — a name, faction, place, or theme.
        max_results: Maximum number of results to return.
    """
    results = _serpapi_search(
        f"site:worldanvil.com eberron {query}", max_results
    )
    if isinstance(results, str):
        return results
    if not results:
        return f"Nothing on World Anvil for: {query!r}."
    return _format_results(
        results,
        max_results,
        "SOURCE: WORLD ANVIL (other DMs' fan creations — NOT canon). "
        "Anything used from here must be clearly labelled as not canon, "
        "with a link.",
    )
