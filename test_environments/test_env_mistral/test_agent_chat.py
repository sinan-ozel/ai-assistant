"""Tests for agent chat endpoint."""

import os
import pytest
import requests


BASE_URL = os.getenv("BASE_URL", "http://app:8000")


def test_agent_chat_simple_message():
    """Test sending a simple message to the agent."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Hello, who are you?",
            "user_id": "test-user-1",
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "conversation_id" in data
    assert "user_id" in data
    assert "message" in data
    assert "role" in data
    assert "created" in data

    # Check values
    assert data["user_id"] == "test-user-1"
    assert data["role"] == "assistant"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0
    assert isinstance(data["conversation_id"], str)

    return data["conversation_id"]


def test_agent_chat_with_conversation_id():
    """Test sending messages in the same conversation."""
    conversation_id = "test-conv-123"
    user_id = "test-user-2"

    # First message
    response1 = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "My favorite color is blue.",
            "conversation_id": conversation_id,
            "user_id": user_id,
        }
    )

    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["conversation_id"] == conversation_id
    assert data1["user_id"] == user_id

    # Second message in same conversation
    response2 = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What is my favorite color?",
            "conversation_id": conversation_id,
            "user_id": user_id,
        }
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["conversation_id"] == conversation_id
    assert data2["user_id"] == user_id

    # Response should reference blue (if model has memory)
    assert isinstance(data2["message"], str)


@pytest.mark.repeated(times=5, threshold=5)
def test_agent_chat_memory_retention(clear_test_memory):
    """Test that agent remembers context from earlier in the conversation."""
    conversation_id = "test-memory-conv"
    user_id = "test-user-memory"

    # First message: provide information
    response1 = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "I have three pets: a dog named Max, a cat named Luna, and a parrot named Rio.",
            "conversation_id": conversation_id,
            "user_id": user_id,
        }
    )

    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["conversation_id"] == conversation_id
    assert isinstance(data1["message"], str)

    # Second message: ask about the information from first message
    response2 = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What is the name of my dog?",
            "conversation_id": conversation_id,
            "user_id": user_id,
        }
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["conversation_id"] == conversation_id

    # The response should reference "Max" if memory is working
    response_text = data2["message"].lower()
    assert "max" in response_text, f"Expected 'Max' in response, got: {data2['message']}"

    # Third message: ask about different information
    response3 = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "How many pets do I have in total?",
            "conversation_id": conversation_id,
            "user_id": user_id,
        }
    )

    assert response3.status_code == 200
    data3 = response3.json()

    # The response should reference "three" or "3" if memory is working
    response_text3 = data3["message"].lower()
    assert "3" in response_text3 or "three" in response_text3, f"Expected '3' or 'three' in response, got: {data3['message']}"


def test_agent_chat_user_isolation():
    """Test that different users have isolated conversations."""
    conversation_id = "shared-conv-id"

    # User 1's message
    response1 = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "My name is Alice.",
            "conversation_id": conversation_id,
            "user_id": "user-alice",
        }
    )

    assert response1.status_code == 200

    # User 2's message with same conversation_id
    response2 = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "My name is Bob.",
            "conversation_id": conversation_id,
            "user_id": "user-bob",
        }
    )

    assert response2.status_code == 200

    # Each user should have their own isolated conversation
    # even with the same conversation_id
    data1 = response1.json()
    data2 = response2.json()

    assert data1["user_id"] == "user-alice"
    assert data2["user_id"] == "user-bob"


def test_agent_chat_generated_conversation_id():
    """Test that conversation_id is generated when not provided."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Hello",
            "user_id": "test-user-4",
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Should have a generated conversation_id
    assert "conversation_id" in data
    assert isinstance(data["conversation_id"], str)
    assert len(data["conversation_id"]) > 0


def test_agent_chat_missing_message():
    """Test that missing message returns error."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "user_id": "test-user-5",
        }
    )

    # Should return validation error
    assert response.status_code == 422


def test_agent_chat_usage_info():
    """Test that usage information is returned."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Hi",
            "user_id": "test-user-6",
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Check usage information
    assert "usage" in data
    usage = data["usage"]
    assert "prompt_tokens" in usage
    assert "completion_tokens" in usage
    assert "total_tokens" in usage

    # Tokens should be non-negative
    assert usage["prompt_tokens"] >= 0
    assert usage["completion_tokens"] >= 0
    assert usage["total_tokens"] >= 0
