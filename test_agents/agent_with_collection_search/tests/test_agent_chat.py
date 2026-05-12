"""Integration tests for agent_with_collection_search.

Verifies that the DSL Search() context manager (capital-S alias) correctly
restricts retrieval to the named collection (shelf1), excluding conflicting
content from shelf2.

The library contains two Markdown files with deliberately contradictory facts
about a fictional city called Nexara:
  shelf1: population 73,400 (flourishing city)
  shelf2: population <= 150 (abandoned settlement)

When Search(input_text, "shelf1") is used, only shelf1 content reaches the model,
so the answer must reflect shelf1 facts.
"""

import os

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.mark.depends(name="test_agent_chat_basic_response", on=["healthy"])
def test_agent_chat_basic_response():
    """Agent responds successfully using the Search DSL with a collection."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Hello!",
            "user_id": "test-collection-1",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "conversation_id" in data
    assert "user_id" in data
    assert "message" in data
    assert "role" in data
    assert "usage" in data
    assert data["user_id"] == "test-collection-1"
    assert data["role"] == "assistant"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


@pytest.mark.depends(on=["test_books_ingested"])
def test_agent_chat_returns_shelf1_facts():
    """Search restricted to shelf1 should return shelf1 facts, not shelf2.

    shelf1/city-guide.md says Nexara has a population of 73,400.
    shelf2/city-guide.md says Nexara had at most 150 inhabitants.

    With Search(input_text, "shelf1"), only shelf1 is searched, so the model
    must report the shelf1 population (73,400 — contains "73").
    """
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What is the population of Nexara?",
            "user_id": "test-collection-shelf1",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert data["role"] == "assistant"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0
    assert "73" in data["message"], (
        f"Expected shelf1 population (73,400) in response; got: {data['message']}"
    )
