import pytest
import requests
import time
import os


BASE_URL = os.getenv("BASE_URL", "http://app:8000")


def test_providers(ollama_server_available):
    """Test if the self-hosted LLM provider is being discovered correctly."""
    url = f"{BASE_URL}/private/v1/providers"
    start = time.time()
    timeout = 5  # seconds
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200 and response.json().get("status", "") == "one_provider_available":
                break
        except Exception:
            pass
        if time.time() - start > timeout:
            raise TimeoutError(f"/private/v1/providers endpoint did not return expected response within {timeout} seconds")
        time.sleep(1)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "one_provider_available"
    assert "available" in data
    assert "default" in data
    assert "total" in data
    assert len(data["available"]) == 1
    # Check for self-hosted provider name (adjust based on your provider config)
    assert data["default"] is not None


