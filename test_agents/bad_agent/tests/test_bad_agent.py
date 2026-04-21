"""Tests verifying that the bad_agent crashes the pod on a chat request.

cortex/chat/prompt.py sends SIGTERM to PID 1 (supervisord), which shuts the
container down. The NameError on the next line surfaces in the logs as a real
Python error before the process exits.
"""

import os
import time

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


def test_pod_is_healthy_before_crash():
    """Confirm the pod starts up correctly before we send a chat."""
    response = requests.get(f"{BASE_URL}/health", timeout=10)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_crashes_pod():
    """Sending a chat should kill the container via SIGTERM to supervisord."""
    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={"message": "Hello", "user_id": "test-bad-1"},
        timeout=30,
    )
    # The NameError is still caught by FastAPI before supervisord finishes
    # shutting down, so we get a 500 back.
    assert response.status_code == 500

    # Poll until the container is unreachable (supervisord stops all processes).
    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
            time.sleep(1)
        except requests.exceptions.ConnectionError:
            return

    pytest.fail("Pod did not crash within 20 seconds after the chat request")
