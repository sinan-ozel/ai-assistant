import os
import time

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.mark.depends(on=["test_health_endpoint.py::test_health_endpoint"])
def test_providers():
    """Test if the local LLM provider is being discovered correctly."""
    url = f"{BASE_URL}/private/v1/providers"
    start = time.time()
    timeout = 60  # seconds - increased to allow for slow provider validation
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                status = response.json().get("status", "")
                # Wait until discovery completes (not initializing anymore)
                if status != "initializing" and status == "ready":
                    break
        except requests.exceptions.RequestException:
            pass
        if time.time() - start > timeout:
            break
        time.sleep(1)
    assert (
        response.status_code == 200
    ), f"/private/v1/providers endpoint did not return expected response within {timeout} seconds"
    data = response.json()
    print(data)
    assert "available" in data
    assert (
        "vision" in data["available"]
    ), f"Expected 'vision' to be in available providers but got {data['available']}"
    assert "default" in data
    assert "total" in data
    assert len(data["available"]) >= 1
    assert (
        data["default"] == "vision"
    ), f"Expected default provider to be 'vision' but got '{data['default']}'"


@pytest.mark.depends(on=["test_providers"])
def test_vision_provider_override():
    """Test that the vision provider is using the overridden configuration from
    cortex/providers/vision.yaml.

    The default vision.yaml points to Mistral API (mistral/pixtral-12b-2409)
    which requires MISTRAL_API_KEY. The overridden vision.yaml in
    cortex/providers points to a self-hosted model (openai/gemma4:e2b).

    If the override is working, this chat request should succeed without
    MISTRAL_API_KEY. If the override is NOT working (using default), this
    request would fail with authentication error.
    """
    url = f"{BASE_URL}/v1/chat/completions"

    response = requests.post(
        url,
        json={
            "model": "vision",  # Explicitly use the vision provider
            "messages": [
                {
                    "role": "user",
                    "content": "Say 'override works' and nothing else.",
                }
            ],
            "max_tokens": 10,
        },
        timeout=180,  # Allow time for the self-hosted model
    )

    # If we're using the default (Mistral), this would fail with 401 or similar auth error
    # If we're using the override (self-hosted), this should succeed with 200
    assert response.status_code == 200, (
        f"Expected 200 (override working), got {response.status_code}. "
        f"Response: {response.text}. "
        f"This suggests the vision provider override from cortex/providers/vision.yaml is not being applied."
    )

    data = response.json()
    assert "choices" in data
    assert len(data["choices"]) > 0
    assert "message" in data["choices"][0]

    # Verify we got a response (proves the self-hosted model is working)
    message_content = data["choices"][0]["message"]["content"]
    assert isinstance(message_content, str)
