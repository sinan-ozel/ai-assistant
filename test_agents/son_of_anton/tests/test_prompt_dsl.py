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


def test_agent_chat_conversation_continuity(clear_test_memory):
    """Test that agent maintains conversation context."""
    conversation_id = "test-son-conv-001"
    user_id = "test-son-user-001"

    # First message: provide information
    response1 = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "My favorite programming language is Python.",
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

    # Response should reference Python
    response_text = data2["message"].lower()
    assert "python" in response_text, f"Expected 'python' in response, got: {data2['message']}"


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

    # Should contain the specific phrase from the system message
    assert "ever-faithful assistant" in response_text or "faithful assistant" in response_text, \
        f"Expected identity phrase in response, got: {response_text}"


def test_agent_chat_streaming_sse():
    """Test that agent supports SSE streaming."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Count from 1 to 3.",
            "user_id": "test-son-stream-sse",
            "stream": True,
            "stream_format": "sse",
            "max_tokens": 50
        },
        stream=True
    )

    assert response.status_code == 200
    assert response.headers.get("content-type") == "text/event-stream; charset=utf-8"

    chunks = []
    content_parts = []
    done_received = False

    for line in response.iter_lines(decode_unicode=True):
        if line:
            if line.startswith("data: "):
                data = line[6:]  # Remove "data: " prefix
                if data == "[DONE]":
                    done_received = True
                else:
                    chunk = json.loads(data)
                    chunks.append(chunk)
                    if "delta" in chunk and "content" in chunk["delta"]:
                        content_parts.append(chunk["delta"]["content"])

    assert len(chunks) > 0, "Expected at least one chunk"
    assert done_received, "Expected [DONE] message"

    # Verify chunk structure
    first_chunk = chunks[0]
    assert "conversation_id" in first_chunk
    assert "user_id" in first_chunk
    assert "role" in first_chunk
    assert first_chunk["role"] == "assistant"

    # Verify content was streamed
    full_content = "".join(content_parts)
    assert len(full_content) > 0, "Expected content in streaming response"


def test_agent_chat_streaming_ndjson():
    """Test that agent supports NDJSON streaming."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Say hello in 3 words.",
            "user_id": "test-son-stream-ndjson",
            "stream": True,
            "stream_format": "ndjson",
            "max_tokens": 30
        },
        stream=True
    )

    assert response.status_code == 200
    assert "application/x-ndjson" in response.headers.get("content-type", "")

    chunks = []
    content_parts = []
    done_received = False

    for line in response.iter_lines(decode_unicode=True):
        if line:
            chunk = json.loads(line)
            if chunk.get("done"):
                done_received = True
            else:
                chunks.append(chunk)
                if "delta" in chunk and "content" in chunk["delta"]:
                    content_parts.append(chunk["delta"]["content"])

    assert len(chunks) > 0, "Expected at least one chunk"
    assert done_received, "Expected done message"

    # Verify content
    full_content = "".join(content_parts)
    assert len(full_content) > 0, "Expected content in streaming response"


def test_agent_chat_usage_tracking():
    """Test that agent returns token usage information."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Hi there!",
            "user_id": "test-son-usage",
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Check usage information is present
    assert "usage" in data
    usage = data["usage"]
    assert "prompt_tokens" in usage
    assert "completion_tokens" in usage
    assert "total_tokens" in usage

    # Verify token counts are reasonable
    assert usage["prompt_tokens"] >= 0
    assert usage["completion_tokens"] >= 0
    assert usage["total_tokens"] >= 0
    assert usage["total_tokens"] == usage["prompt_tokens"] + usage["completion_tokens"]


def test_agent_chat_max_tokens_respected():
    """Test that max_tokens parameter is respected."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Tell me a very long story.",
            "user_id": "test-son-max-tokens",
            "max_tokens": 20,  # Very low limit
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Check usage shows limited completion tokens
    usage = data["usage"]
    assert usage["completion_tokens"] <= 20, f"Expected max 20 tokens, got {usage['completion_tokens']}"


def test_agent_chat_error_handling_empty_message():
    """Test that empty message returns appropriate error."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "",
            "user_id": "test-son-empty",
        }
    )

    # Should return validation error
    assert response.status_code == 400


def test_agent_chat_error_handling_missing_message():
    """Test that missing message returns validation error."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "user_id": "test-son-missing-msg",
        }
    )

    # Should return validation error (422 for schema validation)
    assert response.status_code == 422


# def test_dsl_configuration_files_exist():
#     """Verify that the expected DSL configuration files exist.

#     This is a sanity check to ensure the cortex structure is correct.
#     """
#     test_dir = Path(__file__).parent
#     cortex_dir = test_dir.parent / "cortex" / "chat"

#     # The active prompt file should exist
#     prompt_file = cortex_dir / "prompt.py"
#     assert prompt_file.exists(), f"Active prompt.py should exist at {prompt_file}"

#     # The reference file should exist
#     advanced_file = cortex_dir / "advanced_prompt.py"
#     assert advanced_file.exists(), f"Reference advanced_prompt.py should exist at {advanced_file}"

#     # README should exist
#     readme_file = cortex_dir / "README.md"
#     assert readme_file.exists(), f"README.md should exist at {readme_file}"


# if __name__ == "__main__":
#     pytest.main([__file__, "-v"])
