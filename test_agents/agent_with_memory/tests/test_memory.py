"""Tests for agent_with_memory — verifies MessageHistory retains conversation context."""

import os
import uuid

import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


def test_memory_retention(clear_test_memory):
    """Agent recalls facts stated earlier in the same conversation."""
    conversation_id = f"test-mem-conv-{uuid.uuid4()}"
    user_id = "test-mem-user"

    response1 = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "I have three pets: a dog named Max, a cat named Luna, and a parrot named Rio.",
            "conversation_id": conversation_id,
            "user_id": user_id,
        },
    )
    assert response1.status_code == 200
    assert response1.json()["conversation_id"] == conversation_id

    response2 = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What is the name of my dog?",
            "conversation_id": conversation_id,
            "user_id": user_id,
        },
    )
    assert response2.status_code == 200
    assert "max" in response2.json()["message"].lower(), (
        f"Expected 'Max' in response, got: {response2.json()['message']}"
    )

    response3 = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "How many pets do I have in total?",
            "conversation_id": conversation_id,
            "user_id": user_id,
        },
    )
    assert response3.status_code == 200
    text = response3.json()["message"].lower()
    assert "3" in text or "three" in text, (
        f"Expected '3' or 'three' in response, got: {response3.json()['message']}"
    )
