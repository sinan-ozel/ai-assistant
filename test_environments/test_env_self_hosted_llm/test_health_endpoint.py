import time
import os

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost:11434")
LLAMACPP_HOST = os.getenv("LLAMACPP_HOST", "localhost:8080")


@pytest.mark.depends(name='healthy')
def test_health_endpoint():
    """Test the /health endpoint with retries and timeout."""
    url = f"{BASE_URL}/health"
    start = time.time()
    timeout = 20  # seconds
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200 and response.json().get("status") == "ok":
                break
        except Exception:
            pass
        if time.time() - start > timeout:
            raise TimeoutError(f"/health endpoint did not return expected response within {timeout} seconds")
        time.sleep(1)


@pytest.mark.depends(name='ollama_server_available')
def test_ollama_server_available():
    """Test that the self-hosted Ollama server is reachable and returns models."""
    response = requests.get(f"http://{OLLAMA_HOST}/api/tags", timeout=5)
    assert response.status_code == 200, (
        f"Ollama server at {OLLAMA_HOST} returned {response.status_code}"
    )
    data = response.json()
    assert "models" in data, f"Expected 'models' in response, got: {data}"


@pytest.mark.depends(name='llamacpp_server_available')
def test_llamacpp_server_available():
    """Test that the self-hosted llama.cpp server is reachable and returns models."""
    response = requests.get(f"http://{LLAMACPP_HOST}/v1/models", timeout=5)
    assert response.status_code == 200, (
        f"llama.cpp server at {LLAMACPP_HOST} returned {response.status_code}"
    )
    data = response.json()
    assert "data" in data, f"Expected 'data' in response, got: {data}"
