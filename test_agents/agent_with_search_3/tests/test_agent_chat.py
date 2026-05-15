"""Integration tests for agent_with_search.

Verifies that the DSL search() context manager runs without error and
the agent produces a coherent response (with or without indexed documents).
"""

import os

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.mark.depends(name="test_agent_chat_basic_response", on=["healthy", "test_books_ingested"])
def test_agent_chat_basic_response():
    """Test that the agent responds successfully with the search DSL."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Hello!",
            "user_id": "test-search-1",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "conversation_id" in data
    assert "user_id" in data
    assert "message" in data
    assert "role" in data
    assert "usage" in data
    assert data["user_id"] == "test-search-1"
    assert data["role"] == "assistant"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


@pytest.mark.depends(on=["test_agent_chat_basic_response"])
def test_agent_chat_search_graceful_no_results():
    """Test that the agent handles a query gracefully when no documents are indexed."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What is the capital of France?",
            "user_id": "test-search-2",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


@pytest.mark.depends(on=["test_books_ingested"])
def test_agent_chat_answers_from_library_01():
    """Test that the agent retrieves and uses content from the indexed library.

    Asks a question whose answer is only found in the lycanthropes-in-eberron
    PDF (homebrew D&D 5e content). A correct search-augmented response must
    mention silver, which is the explicit vulnerability of werewolves in all
    forms including hybrid.
    """
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": (
                "According to your library, "
                "which form has the majestic, impressive werewolf look?"
            ),
            "user_id": "test-search-library",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert data["role"] == "assistant"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0
    assert "hybrid" in data["message"].lower(), (
        f"Expected to see 'hybrid' in response; got: {data['message']}"
    )



@pytest.mark.depends(on=["test_books_ingested",
                         "test_agent_chat_answers_from_library_01"])
def test_agent_chat_answers_from_library_02():
    """Test that the agent retrieves and uses content from the indexed library.

    Asks a question whose answer is only found in the lycanthropes-in-eberron
    PDF (homebrew D&D 5e content). A correct search-augmented response must
    mention silver, which is the explicit vulnerability of werewolves in all
    forms including hybrid.
    """
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": (
                "According to your library, "
                "what immunities and vulnerabilities do werewolves have "
                "in the hybrid form?"
            ),
            "user_id": "test-search-library",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert data["role"] == "assistant"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0
    assert "silver" in data["message"].lower(), (
        f"Expected answer to mention silver vulnerability; got: {data['message']}"
    )
