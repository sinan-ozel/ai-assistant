"""Black-box integration tests for multi-tenancy / user isolation.

Two users share the same conversation_id string but must never see each
other's messages. Tests cover both identity mechanisms:

  - user_id in the POST body
  - User-Id HTTP request header

Tests run in a strict linear chain so that any cross-contamination is
caught at the earliest possible step.
"""

import os
import uuid

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")

# Unique per test run so history never accumulates across runs; the isolation
# tests only need the two users to share the same string within one run.
_BODY_CONV = f"test-mt-body-conv-{uuid.uuid4()}"
_HEADER_CONV = f"test-mt-header-conv-{uuid.uuid4()}"

_BODY_ALICE = "test-mt-body-alice"
_BODY_BOB = "test-mt-body-bob"
_HEADER_ALICE = "test-mt-header-alice"
_HEADER_BOB = "test-mt-header-bob"


# ---------------------------------------------------------------------------
# Body user_id isolation
# ---------------------------------------------------------------------------


@pytest.mark.depends(name="test_mt_body_alice_sends", on=["healthy"])
def test_body_alice_sends_name(clear_multi_tenancy_memory):
    """Alice tells the agent her name using user_id in the request body."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "My name is Alice.",
            "user_id": _BODY_ALICE,
            "conversation_id": _BODY_CONV,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == _BODY_ALICE
    assert data["conversation_id"] == _BODY_CONV


@pytest.mark.depends(name="test_mt_body_bob_sends", on=["test_mt_body_alice_sends"])
def test_body_bob_sends_name():
    """Bob tells the agent his name — same conversation_id, different user_id."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "My name is Bob.",
            "user_id": _BODY_BOB,
            "conversation_id": _BODY_CONV,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == _BODY_BOB
    assert data["conversation_id"] == _BODY_CONV


@pytest.mark.depends(name="test_mt_body_alice_recalls", on=["test_mt_body_bob_sends"])
def test_body_alice_recalls_own_name():
    """Alice asks for her name. Response must contain 'alice' and not 'bob'."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What name did I tell you earlier in our conversation?",
            "user_id": _BODY_ALICE,
            "conversation_id": _BODY_CONV,
        },
    )
    assert response.status_code == 200
    reply = response.json()["message"].lower()
    assert "alice" in reply, (
        f"Expected 'alice' in Alice's reply; got: {reply}"
    )
    assert "bob" not in reply, (
        f"Bob's name leaked into Alice's conversation; got: {reply}"
    )


@pytest.mark.depends(name="test_mt_body_bob_recalls", on=["test_mt_body_alice_recalls"])
def test_body_bob_recalls_own_name():
    """Bob asks for his name. Response must contain 'bob' and not 'alice'."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What name did I tell you earlier in our conversation?",
            "user_id": _BODY_BOB,
            "conversation_id": _BODY_CONV,
        },
    )
    assert response.status_code == 200
    reply = response.json()["message"].lower()
    assert "bob" in reply, (
        f"Expected 'bob' in Bob's reply; got: {reply}"
    )
    assert "alice" not in reply, (
        f"Alice's name leaked into Bob's conversation; got: {reply}"
    )


# ---------------------------------------------------------------------------
# Header User-Id isolation
# ---------------------------------------------------------------------------


@pytest.mark.depends(name="test_mt_header_alice_sends", on=["test_mt_body_bob_recalls"])
def test_header_alice_sends_name():
    """Alice tells the agent her name using the User-Id request header."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        headers={"User-Id": _HEADER_ALICE},
        json={
            "message": "My name is Alice.",
            "conversation_id": _HEADER_CONV,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == _HEADER_ALICE
    assert data["conversation_id"] == _HEADER_CONV


@pytest.mark.depends(name="test_mt_header_bob_sends", on=["test_mt_header_alice_sends"])
def test_header_bob_sends_name():
    """Bob tells the agent his name via User-Id header — same conversation_id."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        headers={"User-Id": _HEADER_BOB},
        json={
            "message": "My name is Bob.",
            "conversation_id": _HEADER_CONV,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == _HEADER_BOB
    assert data["conversation_id"] == _HEADER_CONV


@pytest.mark.depends(name="test_mt_header_alice_recalls", on=["test_mt_header_bob_sends"])
def test_header_alice_recalls_own_name():
    """Alice asks for her name via header. Response must contain 'alice' and not 'bob'."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        headers={"User-Id": _HEADER_ALICE},
        json={
            "message": "What name did I tell you earlier in our conversation?",
            "conversation_id": _HEADER_CONV,
        },
    )
    assert response.status_code == 200
    reply = response.json()["message"].lower()
    assert "alice" in reply, (
        f"Expected 'alice' in Alice's reply; got: {reply}"
    )
    assert "bob" not in reply, (
        f"Bob's name leaked into Alice's conversation; got: {reply}"
    )


@pytest.mark.depends(name="test_mt_header_bob_recalls", on=["test_mt_header_alice_recalls"])
def test_header_bob_recalls_own_name():
    """Bob asks for his name via header. Response must contain 'bob' and not 'alice'."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        headers={"User-Id": _HEADER_BOB},
        json={
            "message": "What name did I tell you earlier in our conversation?",
            "conversation_id": _HEADER_CONV,
        },
    )
    assert response.status_code == 200
    reply = response.json()["message"].lower()
    assert "bob" in reply, (
        f"Expected 'bob' in Bob's reply; got: {reply}"
    )
    assert "alice" not in reply, (
        f"Alice's name leaked into Bob's conversation; got: {reply}"
    )


# ---------------------------------------------------------------------------
# Conflict: body user_id and User-Id header disagree
# ---------------------------------------------------------------------------


@pytest.mark.depends(on=["test_mt_header_bob_recalls"])
def test_conflicting_user_id_returns_400():
    """Supplying mismatched user identity in body and header must return 400."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        headers={"User-Id": "test-mt-conflict-header"},
        json={
            "message": "Hello.",
            "user_id": "test-mt-conflict-body",
        },
    )
    assert response.status_code == 400
    detail = response.json().get("detail", "")
    assert "conflict" in detail.lower() or "user" in detail.lower(), (
        f"Expected a descriptive error message; got: {detail}"
    )
