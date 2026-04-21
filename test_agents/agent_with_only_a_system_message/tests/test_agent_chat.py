"""Black-box integration tests for son_of_anton agent.

These tests verify that the agent chat endpoint works correctly
with the son_of_anton DSL configuration by making HTTP requests
and validating responses.
"""

import json
import os
from pathlib import Path

import pytest
import requests


BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.mark.depends(on='healthy', name='test_agent_chat_basic_response')
def test_agent_chat_basic_response():
    """Test that son_of_anton agent responds to basic messages."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Hello, introduce yourself briefly.",
            "user_id": "test-son-of-anton-1",
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "conversation_id" in data
    assert "user_id" in data
    assert "message" in data
    assert "role" in data
    assert "created" in data
    assert "usage" in data

    # Verify basic values
    assert data["user_id"] == "test-son-of-anton-1"
    assert data["role"] == "assistant"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


@pytest.mark.depends(on='test_agent_chat_basic_response')
def test_agent_chat_conversation_continuity(clear_test_memory):
    """Test that agent maintains conversation context."""
    conversation_id = "test-son-conv-001"
    user_id = "test-son-user-001"

    # First message: provide information
    response1 = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "My favorite programming language is Lisp.",
            "conversation_id": conversation_id,
            "user_id": user_id,
        }
    )

    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["conversation_id"] == conversation_id

    # Second message: reference earlier context
    response2 = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What is my favorite programming language?",
            "conversation_id": conversation_id,
            "user_id": user_id,
        }
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["conversation_id"] == conversation_id

    # Response should reference lisp
    response_text = data2["message"].lower()
    assert "lisp" in response_text, f"Expected 'lisp' in response, got: {data2['message']}"


@pytest.mark.depends(on='test_agent_chat_basic_response')
def test_agent_chat_custom_system_message():
    """Test that the custom DSL system message is applied correctly.

    The prompt.py defines a specific identity: "Son of Anton" with
    specific behavior when asked for its name.
    """
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What is your name?",
            "user_id": "test-son-system-msg",
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Response should identify as "Son of Anton"
    response_text = data["message"]
    assert "Son of Anton" in response_text, f"Expected 'Son of Anton' in response, got: {response_text}"
