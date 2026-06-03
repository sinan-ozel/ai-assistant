"""Shared vector-search logic for Qdrant and LanceDB.

Both the ``/private/v1/search`` endpoint and the ``retrieve()`` DSL tool call
this module so that the same query path is exercised regardless of which
storage backend is active.

Collection / table selection mirrors the chunking pipeline:
- Files stored in a subfolder of LIBRARY_DIR land in a collection whose name
  equals the top-level subfolder name.
- Files stored directly under LIBRARY_DIR land in the fallback collection
  (``QDRANT_COLLECTION`` / ``LANCEDB_TABLE``).

When the caller does not specify any collections, the search runs across
**all** existing collections / tables in the active backend.
"""

import logging
import os
import socket
from typing import Any, Optional

import lancedb
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from startup.chunking_pipeline import _chunking_pipeline_state
from startup.pdf_pipeline import _pdf_pipeline_state
from synced_memory import Memory

logger = logging.getLogger(__name__)


# ── Environment-driven defaults (mirrors chunking_pipeline.py) ───────────────

QDRANT_HOST = os.environ.get("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION", "library")

LANCEDB_PATH = os.environ.get("LANCEDB_PATH", "/app/data/lancedb")
LANCEDB_TABLE = os.environ.get("LANCEDB_TABLE", "library")

EMBEDDING_MODEL = os.environ.get(
    "EMBEDDING_MODEL", "nomic-ai/nomic-embed-text-v1.5"
)

DEFAULT_TOP_K = 5

# ── Lazy-loaded in-process embedding model ───────────────────────────────────

_embedding_model = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = TextEmbedding(EMBEDDING_MODEL)
    return _embedding_model


# ── Helper: TCP reachability check ───────────────────────────────────────────


def _qdrant_reachable(
    host: str = QDRANT_HOST,
    port: int = QDRANT_PORT,
    timeout: float = 2.0,
) -> bool:
    """Return True if Qdrant is TCP-reachable."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


# ── Embedding ────────────────────────────────────────────────────────────────


def _embed_query(text: str) -> list[float]:
    """Return the embedding vector for *text* using the in-process fastembed
    model."""
    model = _get_embedding_model()
    return list(next(model.embed([text])))


def ingestion_in_progress() -> bool:
    """Return True if any document is currently being ingested.

    Checks Redis pipeline state for files in active processing stages (Queued,
    Converting, Chunking). Falls back to the in-process global when Redis is
    unavailable.
    """
    _ACTIVE_PDF = {"Queued", "Converting"}
    _ACTIVE_CHUNK = {"Queued", "Chunking"}
    try:
        with Memory() as memory:
            pdf_state: dict = getattr(memory, "pdf_pipeline_state", {}) or {}
            chunk_state: dict = (
                getattr(memory, "chunking_pipeline_state", {}) or {}
            )

        if not pdf_state:
            pdf_state = _pdf_pipeline_state
        if not chunk_state:
            chunk_state = _chunking_pipeline_state

        for entry in pdf_state.values():
            if isinstance(entry, dict) and entry.get("status") in _ACTIVE_PDF:
                return True
        for entry in chunk_state.values():
            if isinstance(entry, dict) and entry.get("status") in _ACTIVE_CHUNK:
                return True
        return False
    except Exception:
        return False


# ── Qdrant helpers ────────────────────────────────────────────────────────────


def _list_qdrant_collections() -> list[str]:
    """Return the names of all Qdrant collections."""
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return [c.name for c in client.get_collections().collections]


def _search_qdrant(
    query_vector: list[float],
    collections: list[str],
    top_k: int,
    filter_payload: Optional[dict],
) -> list[dict[str, Any]]:
    """Run a nearest-neighbour search across one or more Qdrant collections.

    Parameters
    ----------
    query_vector:
        The embedding to search with.
    collections:
        The Qdrant collection names to search.
    top_k:
        Maximum number of results per collection.
    filter_payload:
        Optional Qdrant filter dict.  The dict is converted to a
        ``qdrant_client.http.models.Filter`` object transparently.

    Returns
    -------
    list[dict]
        Each dict contains ``score``, ``collection``, ``text`` (if present
        in the payload), and the remaining payload fields merged in.
    """
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    qdrant_filter: Optional[qmodels.Filter] = None
    if filter_payload:
        conditions = []
        for key, value in filter_payload.items():
            conditions.append(
                qmodels.FieldCondition(
                    key=key,
                    match=qmodels.MatchValue(value=value),
                )
            )
        qdrant_filter = qmodels.Filter(must=conditions)

    results: list[dict[str, Any]] = []
    existing = {c.name for c in client.get_collections().collections}
    for collection in collections:
        if collection not in existing:
            logger.debug(
                "Search: Qdrant collection '%s' does not exist — skipping.",
                collection,
            )
            continue
        hits = client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k,
            query_filter=qdrant_filter,
            with_payload=True,
        )
        for hit in hits:
            payload = hit.payload or {}
            results.append(
                {
                    "score": hit.score,
                    "collection": collection,
                    **payload,
                }
            )

    # Sort combined results across collections by descending score
    results.sort(key=lambda r: r.get("score", 0.0), reverse=True)
    return results[:top_k]


# ── LanceDB helpers ───────────────────────────────────────────────────────────


def _list_lancedb_tables() -> list[str]:
    """Return the names of all LanceDB tables."""
    db = lancedb.connect(LANCEDB_PATH)
    return db.table_names()


def _build_lancedb_where(filter_payload: dict) -> Optional[str]:
    """Convert a flat filter dict to a SQL WHERE clause for LanceDB.

    Only supports equality matches against string / numeric values.
    """
    if not filter_payload:
        return None
    clauses = []
    for key, value in filter_payload.items():
        if isinstance(value, str):
            escaped = value.replace("'", "''")
            clauses.append(f"{key} = '{escaped}'")
        elif isinstance(value, (int, float)):
            clauses.append(f"{key} = {value}")
        else:
            logger.warning(
                "Search: LanceDB filter: unsupported value type %s for key "
                "'%s' — skipping.",
                type(value).__name__,
                key,
            )
    return " AND ".join(clauses) if clauses else None


def _search_lancedb(
    query_vector: list[float],
    tables: list[str],
    top_k: int,
    filter_payload: Optional[dict],
) -> list[dict[str, Any]]:
    """Run a nearest-neighbour search across one or more LanceDB tables.

    Parameters
    ----------
    query_vector:
        The embedding to search with.
    tables:
        The LanceDB table names to search.
    top_k:
        Maximum number of results per table.
    filter_payload:
        Optional equality-filter dict.

    Returns
    -------
    list[dict]
        Each dict contains ``score`` (as ``_distance`` mapped to
        ``score``), ``collection``, and the remaining row fields.
    """
    db = lancedb.connect(LANCEDB_PATH)
    existing = set(db.table_names())
    where_clause = _build_lancedb_where(filter_payload or {})

    results: list[dict[str, Any]] = []
    for table_name in tables:
        if table_name not in existing:
            logger.debug(
                "Search: LanceDB table '%s' does not exist — skipping.",
                table_name,
            )
            continue
        try:
            tbl = db.open_table(table_name)
        except ValueError:
            # table_names() listed the directory but the manifest isn't flushed
            # yet (chunking pipeline concurrent write); treat as not-yet-ready.
            logger.warning(
                "Search: LanceDB table '%s' listed but could not be opened — skipping.",
                table_name,
            )
            continue
        query = tbl.search(query_vector).metric("l2").limit(top_k)
        if where_clause:
            query = query.where(where_clause)
        rows = query.to_list()
        for row in rows:
            # LanceDB returns _distance; normalise to score (lower = better,
            # but we negate so higher is better for consistent sorting).
            distance = row.pop("_distance", None)
            # LanceDB L2 metric returns squared Euclidean distance.
            # For unit-normalised vectors: cosine_similarity = 1 - L2² / 2,
            # which matches Qdrant's cosine score for the same embeddings.
            score = (1.0 - distance / 2.0) if distance is not None else 0.0
            results.append(
                {
                    "score": score,
                    "collection": table_name,
                    **{k: v for k, v in row.items() if k != "vector"},
                }
            )

    results.sort(key=lambda r: r.get("score", 0.0), reverse=True)
    return results[:top_k]


# ── Public API ────────────────────────────────────────────────────────────────


def run_search(
    query: Optional[str],
    collections: Optional[list[str]],
    top_k: int = DEFAULT_TOP_K,
    filter_payload: Optional[dict] = None,
) -> list[dict[str, Any]]:
    """Execute a vector search against Qdrant or LanceDB.

    Qdrant is used when reachable at startup; otherwise LanceDB is the
    fallback.  When *collections* is ``None`` or empty, all collections /
    tables in the active backend are searched.

    Parameters
    ----------
    query:
        Free-text search query.  When provided, the text is embedded and
        used for a nearest-neighbour search.  May be ``None`` when
        *filter_payload* is given (filter-only search).
    collections:
        Explicit list of collection / table names to search.  ``None`` or
        ``[]`` means "search all".
    top_k:
        Maximum total number of results to return.
    filter_payload:
        Optional dict of equality filters applied in addition to the
        vector search.

    Returns
    -------
    list[dict]
        Ordered list of result dicts, each with at least ``score`` and
        ``collection`` keys.

    Raises
    ------
    RuntimeError
        If embedding fails or the vector store raises an unexpected error.
    """
    use_qdrant = _qdrant_reachable()
    backend = "qdrant" if use_qdrant else "lancedb"

    logger.debug(
        "Search: backend=%s query=%r collections=%r top_k=%d filter=%r",
        backend,
        query,
        collections,
        top_k,
        filter_payload,
    )

    # Resolve collection list
    if not collections:
        if use_qdrant:
            collections = _list_qdrant_collections()
        else:
            collections = _list_lancedb_tables()
        logger.debug(
            "Search: resolved collections from %s: %r", backend, collections
        )

    if not collections:
        logger.info("Search: no collections/tables found — returning empty.")
        return []

    # Filter-only search (no query vector needed)
    if query is None:
        if use_qdrant:
            results = _filter_only_qdrant(collections, top_k, filter_payload)
        else:
            results = _filter_only_lancedb(collections, top_k, filter_payload)
        logger.debug("Search: filter-only returned %d result(s).", len(results))
        return results

    # Vector search
    query_vector = _embed_query(query)
    logger.debug("Search: embedding computed, running vector search.")

    if use_qdrant:
        results = _search_qdrant(
            query_vector, collections, top_k, filter_payload
        )
    else:
        results = _search_lancedb(
            query_vector, collections, top_k, filter_payload
        )

    logger.debug(
        "Search: vector search returned %d result(s). Top scores: %s",
        len(results),
        [round(r.get("score", 0.0), 3) for r in results[:3]],
    )
    return results


# ── Filter-only helpers (no embedding needed) ─────────────────────────────────


def _filter_only_qdrant(
    collections: list[str],
    top_k: int,
    filter_payload: Optional[dict],
) -> list[dict[str, Any]]:
    """Scroll Qdrant by filter without a query vector."""
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    qdrant_filter: Optional[qmodels.Filter] = None
    if filter_payload:
        conditions = []
        for key, value in filter_payload.items():
            conditions.append(
                qmodels.FieldCondition(
                    key=key,
                    match=qmodels.MatchValue(value=value),
                )
            )
        qdrant_filter = qmodels.Filter(must=conditions)

    results: list[dict[str, Any]] = []
    existing = {c.name for c in client.get_collections().collections}
    for collection in collections:
        if collection not in existing:
            continue
        points, _ = client.scroll(
            collection_name=collection,
            scroll_filter=qdrant_filter,
            limit=top_k,
            with_payload=True,
        )
        for point in points:
            payload = point.payload or {}
            results.append({"score": 1.0, "collection": collection, **payload})

    return results[:top_k]


def _filter_only_lancedb(
    tables: list[str],
    top_k: int,
    filter_payload: Optional[dict],
) -> list[dict[str, Any]]:
    """Scan LanceDB by filter without a query vector."""
    db = lancedb.connect(LANCEDB_PATH)
    existing = set(db.table_names())
    where_clause = _build_lancedb_where(filter_payload or {})

    results: list[dict[str, Any]] = []
    for table_name in tables:
        if table_name not in existing:
            continue
        try:
            tbl = db.open_table(table_name)
        except ValueError:
            logger.warning(
                "Search: LanceDB table '%s' listed but could not be opened — skipping.",
                table_name,
            )
            continue
        query = tbl.search().limit(top_k)
        if where_clause:
            query = query.where(where_clause)
        rows = query.to_list()
        for row in rows:
            row.pop("_distance", None)
            results.append(
                {
                    "score": 1.0,
                    "collection": table_name,
                    **{k: v for k, v in row.items() if k != "vector"},
                }
            )

    return results[:top_k]
