import logging
import re

import httpx

logger = logging.getLogger(__name__)

_MAX_CHARS = 8000
_UA = "Mozilla/5.0 (compatible; eberron-dm-assistant/0.1)"


@tool.mcp(title="Read Web Page", read_only_hint=True, open_world_hint=True)
def read_web_page(url: str = "https://keith-baker.com/") -> str:
    """Fetch a web page and return its text content.

    Use this to read a promising link from one of the search tools when
    the snippet is not enough. The canonicity of the content is that of
    the site it came from — keep the label from the search tool.

    Args:
        url: Full URL of the page to read.
    """
    try:
        response = httpx.get(
            url,
            headers={"User-Agent": _UA},
            follow_redirects=True,
            timeout=15.0,
        )
        response.raise_for_status()
        html = response.text
    except Exception as exc:
        logger.error("read_web_page: fetch failed for %s: %s", url, exc)
        return f"Could not read {url}: {exc}"

    # Strip scripts, styles, and tags; collapse whitespace.
    text = re.sub(
        r"<(script|style|noscript)\b.*?</\1>", " ", html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return f"Page at {url} contained no readable text."
    if len(text) > _MAX_CHARS:
        text = text[:_MAX_CHARS] + " …[truncated]"
    return f"Content of {url}:\n{text}"
