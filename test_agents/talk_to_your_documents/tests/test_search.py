"""Tests for POST /private/v1/search."""

import json
import os
import time

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

RETRY_TIMEOUT = 120  # seconds to wait for embedding to become available


def _search_with_retry(payload: dict, timeout: int = RETRY_TIMEOUT) -> requests.Response:
    """POST to /private/v1/search, retrying on 503 (embedding busy) up to *timeout* seconds."""
    start = time.time()
    while True:
        resp = requests.post(
            f"{BASE_URL}/private/v1/search",
            json=payload,
            stream=payload.get("stream", True),
        )
        if resp.status_code != 503:
            return resp
        retry_after = int(resp.headers.get("Retry-After", "15"))
        if time.time() - start > timeout:
            return resp
        time.sleep(retry_after)


@pytest.mark.depends(on=["healthy"])
def test_search_never_returns_500():
    """Search must not crash with 500 regardless of ingestion state.

    Runs immediately after startup (before ingestion completes). Acceptable
    responses are 200 (empty or partial results) and 503 (embedding busy).
    """
    resp = requests.post(
        f"{BASE_URL}/private/v1/search",
        json={"query": "psionic powers", "top_k": 1},
        stream=True,
    )
    assert resp.status_code in (200, 503), (
        f"Expected 200 or 503, got {resp.status_code}: {resp.text[:200]}"
    )
    if resp.status_code == 503:
        assert "Retry-After" in resp.headers, "503 response must include Retry-After header"
        body = resp.json()
        assert "detail" in body, "503 response must include detail message"


@pytest.mark.depends(on=["test_books_endpoint"])
def test_search_returns_results_as_expected():
    """POST /private/v1/search should return NDJSON results for a text query.

    Depends on test_books_endpoint so all PDFs are already chunked before
    this runs. Retries on 503 in case the embedding service is temporarily
    busy from a pipeline re-run.
    """
    resp = _search_with_retry({"query": "psionic powers", "top_k": 3})
    assert resp.status_code == 200, (
        f"Expected 200, got {resp.status_code}: {resp.text}"
    )

    lines = [line for line in resp.iter_lines() if line]
    parsed = [json.loads(line) for line in lines]

    print("\n=== /private/v1/search results ===")
    for item in parsed:
        print(json.dumps(item, indent=2))
    print("===================================\n")

    # Last line should be the done sentinel
    assert parsed[-1].get("done") is True, (
        'Last NDJSON line should be {"done": true}'
    )

    results = [p for p in parsed if not p.get("done")]
    assert results, "Expected at least one search result"

    for result in results:
        assert "score" in result, f"Result missing 'score': {result}"
        assert "collection" in result, f"Result missing 'collection': {result}"
        assert isinstance(result["score"], (int, float))
        assert "file_path" in result, f"Result missing 'file_path': {result}"
        assert "section_title" in result, f"Result missing 'section_title': {result}"
        assert "text" in result, f"Result missing 'text': {result}"
        assert len(result["text"]) > 0, f"Result 'text' is empty: {result}"
        assert "book" in result, f"Result missing 'book': {result}"
        assert isinstance(result["book"], dict), f"'book' should be a dict: {result}"
        assert "tags" in result["book"], f"'book' missing 'tags': {result}"
        assert isinstance(result["book"]["tags"], list), f"'book.tags' should be a list: {result}"

    top = results[0]
    assert top["collection"].startswith("shelf"), f"Top result collection should start with 'shelf': {top}"
    assert top["file_path"] == "shelf1/simple-psionics.pdf", (
        f"Top result file_path should be 'shelf1/simple-psionics.pdf': {top}"
    )
    assert round(top["score"], 2) == 0.48, (
        f"Top result score should be 0.48: {top['score']}"
    )


@pytest.mark.depends(on=["test_books_endpoint"])
def test_search_with_collection():
    """Search restricted to a specific collection should succeed."""
    resp = _search_with_retry({"query": "psionic", "collection": "shelf1", "top_k": 3})
    assert resp.status_code == 200, (
        f"Expected 200, got {resp.status_code}: {resp.text}"
    )

    lines = [line for line in resp.iter_lines() if line]
    parsed = [json.loads(line) for line in lines]
    assert parsed[-1].get("done") is True


@pytest.mark.depends(on=["healthy"])
def test_search_missing_query_and_filter_returns_400():
    """POST /private/v1/search with neither query nor filter should return 400."""
    resp = requests.post(
        f"{BASE_URL}/private/v1/search",
        json={"top_k": 5},
    )
    assert resp.status_code == 400, (
        f"Expected 400, got {resp.status_code}: {resp.text}"
    )


@pytest.mark.depends(on=["healthy"])
def test_search_both_collection_and_collections_returns_400():
    """Providing both 'collection' and 'collections' should return 400."""
    resp = requests.post(
        f"{BASE_URL}/private/v1/search",
        json={
            "query": "test",
            "collection": "shelf1",
            "collections": ["shelf1", "shelf2"],
        },
    )
    assert resp.status_code == 400, (
        f"Expected 400, got {resp.status_code}: {resp.text}"
    )


@pytest.mark.depends(on=["test_books_endpoint"])
def test_search_with_filter():
    """Filter-only search (no query) should return matching rows."""
    resp = _search_with_retry(
        {"filter": {"file_path": "shelf1/simple-psionics.pdf"}, "top_k": 5}
    )
    assert resp.status_code == 200, (
        f"Expected 200, got {resp.status_code}: {resp.text}"
    )

    lines = [line for line in resp.iter_lines() if line]
    parsed = [json.loads(line) for line in lines]
    assert parsed[-1].get("done") is True


@pytest.mark.depends(on=["test_books_endpoint"])
def test_search_stream_false():
    """POST /private/v1/search with stream=false should return a JSON array.

    Verifies that the endpoint returns a standard JSON array (not NDJSON)
    when stream=false is passed in the request body.
    """
    resp = _search_with_retry({"query": "psionic powers", "top_k": 3, "stream": False})
    assert resp.status_code == 200, (
        f"Expected 200, got {resp.status_code}: {resp.text}"
    )

    results = resp.json()

    print("\n=== /private/v1/search (stream=false) results ===")
    for item in results:
        print(json.dumps(item, indent=2))
    print("===================================\n")

    assert isinstance(results, list), f"Expected a JSON array, got: {type(results)}"
    assert results, "Expected at least one search result"

    for result in results:
        assert "score" in result, f"Result missing 'score': {result}"
        assert "collection" in result, f"Result missing 'collection': {result}"
        assert isinstance(result["score"], (int, float))
        assert "file_path" in result, f"Result missing 'file_path': {result}"
        assert "section_title" in result, f"Result missing 'section_title': {result}"
        assert "text" in result, f"Result missing 'text': {result}"
        assert len(result["text"]) > 0, f"Result 'text' is empty: {result}"
        assert "book" in result, f"Result missing 'book': {result}"
        assert isinstance(result["book"], dict), f"'book' should be a dict: {result}"
        assert "tags" in result["book"], f"'book' missing 'tags': {result}"
        assert isinstance(result["book"]["tags"], list), (
            f"'book.tags' should be a list: {result}"
        )

    top = results[0]
    assert top["collection"].startswith("shelf"), (
        f"Top result collection should start with 'shelf': {top}"
    )
    assert top["file_path"] == "shelf1/simple-psionics.pdf", (
        f"Top result file_path should be 'shelf1/simple-psionics.pdf': {top}"
    )
