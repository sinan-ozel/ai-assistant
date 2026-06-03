"""Tests for the Anthropic agent chat endpoint."""

import os

import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


def test_anthropic_agent_simple_message(anthropic_api_key_available):
    """Test sending a simple message to the Anthropic agent."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Hello! Please respond with a single sentence.",
            "user_id": "test-anthropic-1",
            "max_tokens": 64,
        },
        timeout=120,
    )

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )
    data = response.json()

    assert "conversation_id" in data
    assert "user_id" in data
    assert "message" in data
    assert "role" in data
    assert "created" in data

    assert data["user_id"] == "test-anthropic-1"
    assert data["role"] == "assistant"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


def test_anthropic_agent_conversation(
    anthropic_api_key_available, clear_test_memory
):
    """Test a multi-turn conversation with the Anthropic agent."""
    conversation_id = "test-anthropic-conv-1"
    user_id = "test-anthropic-conv-user"

    response1 = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "My favorite number is 42.",
            "conversation_id": conversation_id,
            "user_id": user_id,
            "max_tokens": 64,
        },
        timeout=120,
    )
    assert response1.status_code == 200

    response2 = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What is my favorite number?",
            "conversation_id": conversation_id,
            "user_id": user_id,
            "max_tokens": 64,
        },
        timeout=120,
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert "42" in data2["message"], (
        f"Expected '42' in response, got: {data2['message']}"
    )


def test_anthropic_agent_response_usage(anthropic_api_key_available):
    """Test that usage information is returned."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Say hi.",
            "user_id": "test-anthropic-usage",
            "max_tokens": 32,
        },
        timeout=120,
    )

    assert response.status_code == 200
    data = response.json()

    assert "usage" in data
    usage = data["usage"]
    assert "prompt_tokens" in usage
    assert "completion_tokens" in usage
    assert "total_tokens" in usage
    assert usage["prompt_tokens"] >= 0
    assert usage["completion_tokens"] >= 0
    assert usage["total_tokens"] >= 0
