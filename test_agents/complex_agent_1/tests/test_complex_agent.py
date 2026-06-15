"""Integration tests for complex_agent_1.

This agent exercises the multi-llm() pipeline in prompt.py:
  1. llm() — extract search terms (uses provider YAML temperature=0.3)
  2. llm(provider="default") — classify intent, score 1–10
  3. Search(extracted_terms) — vector search
  4. llm(temperature=computed) — final answer with temperature override

Tests verify:
  - The three-call pipeline completes without error.
  - provider= kwarg (explicit "default") does not break the call.
  - temperature= override is accepted and does not cause an error.
  - Search results are incorporated: factual questions draw on library content.
  - Creative questions (high-temperature path) also complete without error.
"""

import os

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


def _chat(message, user_id, conversation_id=None, timeout=120):
    payload = {"message": message, "user_id": user_id}
    if conversation_id:
        payload["conversation_id"] = conversation_id
    return requests.post(f"{BASE_URL}/v1/agent/chat", json=payload, timeout=timeout)


# ── Pipeline smoke tests ────────────────────────────────────────────────────

@pytest.mark.depends(on=["healthy"], name="test_pipeline_completes")
def test_pipeline_completes(clear_test_memory):
    """Three-call llm() pipeline returns a valid, non-empty response."""
    resp = _chat("Hello, what is Eberron?", "test-complex-smoke")
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "assistant"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0
    assert "conversation_id" in data
    assert "usage" in data


@pytest.mark.depends(on=["test_pipeline_completes"])
def test_response_shape(clear_test_memory):
    """Response body contains all required fields."""
    resp = _chat("Tell me about the Mournland.", "test-complex-shape")
    assert resp.status_code == 200
    data = resp.json()
    for field in ("conversation_id", "user_id", "message", "role", "usage"):
        assert field in data, f"Missing field: {field}"
    assert data["user_id"] == "test-complex-shape"


# ── provider= kwarg ─────────────────────────────────────────────────────────

@pytest.mark.depends(on=["test_pipeline_completes"])
def test_explicit_provider_default_does_not_error(clear_test_memory):
    """llm(provider='default') in the prompt does not cause a 500.

    The classification step in prompt.py calls llm(..., provider='default').
    This verifies that the explicit provider kwarg is accepted and routed
    correctly when the value is 'default'.
    """
    resp = _chat("Who are the Dragonmarked Houses?", "test-complex-provider")
    assert resp.status_code == 200
    assert resp.json()["role"] == "assistant"


# ── temperature= override ───────────────────────────────────────────────────

@pytest.mark.depends(on=["test_pipeline_completes"])
def test_temperature_override_factual_path(clear_test_memory):
    """A clearly factual question routes through a low temperature (≈0.1).

    The prompt.py maps score=1 → temperature=0.1, overriding the provider
    YAML default of 0.3. We verify the call completes without error.
    """
    resp = _chat(
        "What is the capital of Breland and who rules it?",
        "test-complex-temp-low",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["message"]) > 0


@pytest.mark.depends(on=["test_pipeline_completes"])
def test_temperature_override_creative_path(clear_test_memory):
    """A clearly creative request routes through a high temperature (≈0.9).

    The prompt.py maps score=10 → temperature=0.9, overriding the provider
    YAML default of 0.3. We verify the call completes without error.
    """
    resp = _chat(
        "Invent a brand-new NPC: a changeling spy working for the Boromar Clan.",
        "test-complex-temp-high",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["message"]) > 0


# ── Search integration ──────────────────────────────────────────────────────

@pytest.mark.depends(on=["test_books_ingested", "test_pipeline_completes"])
def test_factual_question_uses_library(clear_test_memory):
    """Factual question about lycanthropes draws on indexed library content.

    The question quotes the library's own phrasing to make retrieval reliable.
    The final answer must mention 'hybrid' or 'majestic' — both appear only
    in the Hybrid Form section of the library PDF.
    """
    resp = _chat(
        "According to your library, which form is described as the majestic, impressive werewolf look?",
        "test-complex-library-1",
    )
    assert resp.status_code == 200
    data = resp.json()
    msg = data["message"].lower()
    assert "hybrid" in msg or "majestic" in msg, (
        f"Expected 'hybrid' or 'majestic' in response; got: {data['message']}"
    )


@pytest.mark.depends(
    on=["test_books_ingested", "test_factual_question_uses_library"]
)
def test_vulnerability_question_uses_library(clear_test_memory):
    """Silver vulnerability for werewolves in hybrid form comes from the library.

    This tests that the extracted search terms (e.g. 'silver', 'vulnerability',
    'hybrid', 'werewolf') return the right chunks, and the final answer
    correctly surfaces the silver vulnerability.
    """
    resp = _chat(
        "According to your library, "
        "what immunities and vulnerabilities do werewolves have in hybrid form?",
        "test-complex-library-2",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "silver" in data["message"].lower(), (
        f"Expected 'silver' in response; got: {data['message']}"
    )


# ── Multi-turn ──────────────────────────────────────────────────────────────

@pytest.mark.depends(on=["test_pipeline_completes"])
def test_multi_turn_conversation(clear_test_memory):
    """Conversation history is preserved across turns in the same session."""
    first = _chat("My name is Mordain.", "test-complex-multi")
    assert first.status_code == 200
    conv_id = first.json()["conversation_id"]

    second = _chat("What is my name?", "test-complex-multi", conv_id)
    assert second.status_code == 200
    assert "mordain" in second.json()["message"].lower(), (
        f"Expected name recall; got: {second.json()['message']}"
    )
