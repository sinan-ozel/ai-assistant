"""Vector search endpoint.

POST /private/v1/search

Streams search results as NDJSON.  Delegates all vector-store logic to
``common.search`` so the same code path is exercised by both this endpoint
and the ``retrieve()`` DSL tool.
"""

import json
import logging

from common.search import (
    DEFAULT_TOP_K,
    EmbeddingUnavailableError,
    ingestion_in_progress,
    run_search,
)
from fastapi import HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

logger = logging.getLogger(__name__)


async def handler(request: dict):
    """Search the vector store.

    Either ``query`` or ``filter`` (or both) must be supplied.
    ``collection`` and ``collections`` are mutually exclusive.

    When ``stream`` is ``True`` (the default), results are streamed as NDJSON.
    When ``stream`` is ``False``, results are returned as a JSON array.
    """
    query: str | None = request.get("query")
    collection: str | None = request.get("collection")
    collections: list[str] | None = request.get("collections")
    top_k: int = int(request.get("top_k", DEFAULT_TOP_K))
    filter_payload: dict | None = request.get("filter")
    stream: bool = request.get("stream", True)

    # --- Validate request ------------------------------------------------
    if query is None and not filter_payload:
        raise HTTPException(
            status_code=400,
            detail="At least one of 'query' or 'filter' must be provided.",
        )

    if collection is not None and collections is not None:
        raise HTTPException(
            status_code=400,
            detail=(
                "'collection' and 'collections' are mutually exclusive. "
                "Provide at most one."
            ),
        )

    # Normalise to a single list (or None = search all)
    resolved_collections: list[str] | None = None
    if collection is not None:
        resolved_collections = [collection]
    elif collections is not None:
        resolved_collections = list(collections)

    logger.info(
        "Search: query=%r collections=%r top_k=%d filter=%r",
        query,
        resolved_collections,
        top_k,
        filter_payload,
    )

    try:
        results = run_search(
            query=query,
            collections=resolved_collections,
            top_k=top_k,
            filter_payload=filter_payload,
        )
    except EmbeddingUnavailableError:
        if ingestion_in_progress():
            detail = (
                "Document ingestion is in progress. "
                "The embedding service is busy — try again in 15 seconds."
            )
        else:
            detail = (
                "The embedding service is unavailable. "
                "Try again in 15 seconds."
            )
        return JSONResponse(
            status_code=503,
            content={"detail": detail},
            headers={"Retry-After": "15"},
        )

    if not stream:
        return JSONResponse(content=results)

    async def generate():
        for result in results:
            yield json.dumps(result, default=str) + "\n"
        yield json.dumps({"done": True}) + "\n"

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


spec = {
    "path": "/private/v1/search",
    "methods": ["POST"],
    "summary": "Search the vector store",
    "description": (
        "Perform a vector search against the indexed document library. "
        "Uses Qdrant when available, falls back to LanceDB otherwise. "
        "When 'stream' is true (default), results are streamed as NDJSON. "
        "When 'stream' is false, results are returned as a JSON array. "
        "Either 'query' or 'filter' (or both) must be provided. "
        "'collection' and 'collections' are mutually exclusive."
    ),
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "Free-text search query. Embedded and used "
                                "for nearest-neighbour search."
                            ),
                        },
                        "collection": {
                            "type": "string",
                            "description": (
                                "Single collection / table to search. "
                                "Mutually exclusive with 'collections'."
                            ),
                        },
                        "collections": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "List of collections / tables to search. "
                                "Mutually exclusive with 'collection'. "
                                "Omit to search all available collections."
                            ),
                        },
                        "top_k": {
                            "type": "integer",
                            "minimum": 1,
                            "default": DEFAULT_TOP_K,
                            "description": "Maximum number of results to return.",
                        },
                        "filter": {
                            "type": "object",
                            "description": (
                                "Optional equality-filter dict applied in "
                                "addition to the vector search. Keys are "
                                "payload / column names; values are the "
                                "required values."
                            ),
                        },
                        "stream": {
                            "type": "boolean",
                            "default": True,
                            "description": (
                                "When true (the default), results are streamed "
                                "as NDJSON. When false, results are returned as "
                                "a JSON array."
                            ),
                        },
                    },
                },
                "example": {
                    "query": "psionic powers telepathy",
                    "top_k": 5,
                    "stream": False,
                },
            }
        },
    },
    "responses": {
        200: {
            "description": (
                "Search results streamed as NDJSON. Each line is a JSON "
                "object with at least 'score' and 'collection' keys. The "
                'final line is {"done": true}.'
            ),
            "content": {
                "application/x-ndjson": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "score": {
                                "type": "number",
                                "description": "Relevance score (higher is better).",
                            },
                            "collection": {
                                "type": "string",
                                "description": (
                                    "Collection / table the result came from."
                                ),
                            },
                            "text": {
                                "type": "string",
                                "description": "Chunk text (if stored in payload).",
                            },
                            "done": {
                                "type": "boolean",
                                "description": (
                                    "Present and true only on the final "
                                    "sentinel line."
                                ),
                            },
                        },
                    },
                    "example": {
                        "score": 0.92,
                        "collection": "shelf1",
                        "text": "Telepathy is a psionic power ...",
                        "section_title": "Telepathy",
                        "file_path": "shelf1/simple-psionics.pdf",
                    },
                }
            },
        },
        400: {
            "description": (
                "Bad request — missing both 'query' and 'filter', or "
                "both 'collection' and 'collections' provided."
            ),
        },
        503: {
            "description": (
                "Service unavailable — the embedding service is temporarily "
                "busy (e.g. document ingestion in progress). "
                "Retry after the number of seconds indicated in Retry-After."
            ),
        },
    },
}
