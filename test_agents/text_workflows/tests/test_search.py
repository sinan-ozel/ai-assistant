"""Tests for POST /private/v1/search with no library configured.

Verifies that the search endpoint returns an empty result set (not an error)
when no documents have been ingested.
"""

import json
import os

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


@pytest.mark.depends(on=["healthy"])
def test_search_returns_empty_when_no_library():
    """Search should return 200 with no results when no library is configured.

    No documents are ingested for this agent so there are no collections in the
    vector store. The endpoint should return an empty NDJSON stream (just the
    done sentinel) rather than an error.
    """
    resp = requests.post(
        f"{BASE_URL}/private/v1/search",
        json={"query": "psionic powers", "top_k": 5},
        stream=True,
    )
    assert (
        resp.status_code == 200
    ), f"Expected 200, got {resp.status_code}: {resp.text}"

    lines = [line for line in resp.iter_lines() if line]
    parsed = [json.loads(line) for line in lines]
    assert (
        parsed[-1].get("done") is True
    ), 'Last NDJSON line should be {"done": true}'
    results = [p for p in parsed if not p.get("done")]
    assert results == [], f"Expected no results, got: {results}"


@pytest.mark.depends(on=["healthy"])
def test_search_stream_false_returns_empty_list_when_no_library():
    """Search with stream=false should return an empty JSON array when no
    library."""
    resp = requests.post(
        f"{BASE_URL}/private/v1/search",
        json={"query": "anything", "top_k": 5, "stream": False},
    )
    assert (
        resp.status_code == 200
    ), f"Expected 200, got {resp.status_code}: {resp.text}"
    results = resp.json()
    assert isinstance(results, list), f"Expected a list, got: {type(results)}"
    assert results == [], f"Expected empty list, got: {results}"
