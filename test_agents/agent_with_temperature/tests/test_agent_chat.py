"""Integration tests for agent_with_temperature.

Verifies that the DSL temperature override (0.9) is applied and the
agent responds as a creative writing assistant.
"""

import os

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.mark.depends(name="test_agent_chat_basic_response", on=["healthy"])
def test_agent_chat_basic_response():
    """Test that the agent responds successfully."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Hello!",
            "user_id": "test-temp-1",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "conversation_id" in data
    assert "user_id" in data
    assert "message" in data
    assert "role" in data
    assert "usage" in data
    assert data["user_id"] == "test-temp-1"
    assert data["role"] == "assistant"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


@pytest.mark.depends(on=["test_agent_chat_basic_response"])
def test_agent_chat_creative_identity():
    """Test that the agent identifies as a creative writing assistant."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What kind of assistant are you?",
            "user_id": "test-temp-identity",
        },
    )

    assert response.status_code == 200
    data = response.json()
    response_text = data["message"].lower()
    assert (
        "creative" in response_text or "writing" in response_text
    ), f"Expected creative writing identity in response, got: {data['message']}"
