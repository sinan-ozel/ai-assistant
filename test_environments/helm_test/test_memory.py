import os
import uuid

import requests

BASE_URL = os.environ.get("BASE_URL", "http://host.docker.internal:8000")


def test_agent_memory():
    conversation_id = str(uuid.uuid4())

    resp1 = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "My secret word is PINEAPPLE.",
            "conversation_id": conversation_id,
            "user_id": "helm-test-memory",
        },
        timeout=60,
    )
    assert resp1.status_code == 200, f"First message failed: {resp1.text}"

    resp2 = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "What is my secret word?",
            "conversation_id": conversation_id,
            "user_id": "helm-test-memory",
        },
        timeout=60,
    )
    assert resp2.status_code == 200, f"Second message failed: {resp2.text}"
    body = resp2.json()
    assert "PINEAPPLE" in body["message"].upper(), (
        f"Agent did not recall the secret word. Response: {body['message']}"
    )
