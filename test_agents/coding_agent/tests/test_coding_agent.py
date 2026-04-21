"""Tests for the coding agent using Mistral Codestral."""

import os
import re

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")

_FENCE_RE = re.compile(r"```[\w]*\n(.*?)```", re.DOTALL)


def extract_fenced_code(text: str) -> list[str]:
    """Return a list of non-empty code blocks extracted from markdown fences."""
    return [block.strip() for block in _FENCE_RE.findall(text) if block.strip()]


def test_coding_agent_returns_code():
    """Test that the coding agent returns a code snippet for a coding question."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Write a Python function that returns the sum of a list of numbers.",
            "user_id": "test-coding-1",
            "max_tokens": 256,
        },
        timeout=120,
    )

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )
    data = response.json()

    assert "message" in data
    assert data["role"] == "assistant"
    reply = data["message"]
    assert isinstance(reply, str)
    assert len(reply) > 0

    blocks = extract_fenced_code(reply)
    assert len(blocks) > 0, (
        f"Expected at least one fenced code block in reply, got: {reply[:300]}"
    )
    assert any("def " in block for block in blocks), (
        f"Expected a function definition inside a code fence, got blocks: {blocks}"
    )



def test_coding_agent_override_is_active():
    """Test that the _override DSL is applied: agent responds as coding assistant."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What is your role?",
            "user_id": "test-coding-2",
            "max_tokens": 128,
        },
        timeout=120,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "assistant"
    reply = data["message"]
    assert isinstance(reply, str)
    assert len(reply) > 0
    assert "coding" in reply.lower(), "Expected `coding` to be in the response, got: {reply}"


def test_coding_agent_response_structure():
    """Test that the agent chat response has the expected structure."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "How do I reverse a string in Python?",
            "user_id": "test-coding-3",
            "max_tokens": 128,
        },
        timeout=120,
    )

    assert response.status_code == 200
    data = response.json()

    assert "conversation_id" in data
    assert "user_id" in data
    assert "message" in data
    assert "role" in data
    assert "created" in data
    assert "usage" in data

    assert data["user_id"] == "test-coding-3"
    assert data["role"] == "assistant"

    usage = data["usage"]
    assert "prompt_tokens" in usage
    assert "completion_tokens" in usage
    assert "total_tokens" in usage

    reply = data["message"]
    assert isinstance(reply, str)
    assert len(reply) > 0
    print(reply)

    blocks = extract_fenced_code(reply)
    assert len(blocks) > 0, (
        f"Expected at least one fenced code block in reply, got: {reply[:300]}"
    )
    assert any(" = " in block for block in blocks), (
        f"Expected an equal sign inside a code fence, got blocks: {blocks}"
    )
