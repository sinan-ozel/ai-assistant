import os
import time
import uuid

import requests

BASE_URL = os.environ.get("BASE_URL", "http://host.docker.internal:8000")

# Provider rate limits (429) are not release defects — retry with a pause
# instead of failing the post-release run.
_RATE_LIMIT_RETRIES = 3
_RATE_LIMIT_DELAY = 15.0


def _post_chat(payload: dict) -> requests.Response:
    for attempt in range(_RATE_LIMIT_RETRIES + 1):
        response = requests.post(
            f"{BASE_URL}/v1/agent/chat", json=payload, timeout=60
        )
        if response.status_code != 429 or attempt == _RATE_LIMIT_RETRIES:
            return response
        time.sleep(_RATE_LIMIT_DELAY)
    return response


def test_agent_memory():
    conversation_id = str(uuid.uuid4())

    resp1 = _post_chat(
        {
            "message": "My secret word is PINEAPPLE.",
            "conversation_id": conversation_id,
            "user_id": "helm-test-memory",
        }
    )
    assert resp1.status_code == 200, f"First message failed: {resp1.text}"

    resp2 = _post_chat(
        {
            "message": "What is my secret word?",
            "conversation_id": conversation_id,
            "user_id": "helm-test-memory",
        }
    )
    assert resp2.status_code == 200, f"Second message failed: {resp2.text}"
    body = resp2.json()
    assert "PINEAPPLE" in body["message"].upper(), (
        f"Agent did not recall the secret word. Response: {body['message']}"
    )
