import pytest
import requests
import time
import os


BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.mark.depends(on=['ollama_server_available',
                         'healthy'],
                     name='providers_loaded')
def test_providers():
    """Test if the self-hosted LLM provider is being discovered correctly."""
    url = f"{BASE_URL}/private/v1/providers"
    start = time.time()
    timeout = 5  # seconds
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200 and response.json().get("status", "") == "ready":
                break
        except requests.exceptions.RequestException:
            pass
        if time.time() - start > timeout:
            break
        time.sleep(1)
    assert response.status_code == 200, f"/private/v1/providers endpoint did not return expected response within {timeout} seconds"
    data = response.json()
    print(data)
    assert data["status"] == "ready", f"Expected status 'ready' but got '{data['status']}'"
    assert "available" in data
    assert "default" in data
    assert "total" in data
    assert len(data["available"]) == 1
    # Check for self-hosted provider name (adjust based on your provider config)
    assert data["default"] == 'default', f"Expected default provider to be 'default' but got '{data['default']}'"


@pytest.mark.depends(on=['ollama_server_available'], name='test_provider_context_window')
def test_provider_context_window():
    """Test if the provider's context window endpoint works correctly."""
    # First get the list of providers
    providers_url = f"{BASE_URL}/private/v1/providers"
    response = requests.get(providers_url)
    assert response.status_code == 200
    data = response.json()

    # Get the default provider name
    provider_name = data["default"]
    assert provider_name is not None

    # Query the context window endpoint
    context_url = f"{BASE_URL}/private/v1/providers/{provider_name}/max-context-window"
    start = time.time()
    timeout = 30  # seconds - context window query can take time
    response = None
    while True:
        try:
            response = requests.get(context_url)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            pass
        if time.time() - start > timeout:
            break
        time.sleep(1)

    assert response is not None, f"No response received from {context_url}"

    # # Unfortunately, context window does not work with llama.cpp
    # assert response.status_code in [200, 404], (
    #     f"Context window endpoint did not return 200 or 404 within {timeout} seconds. "
    #     f"Status: {response.status_code}, Response: {response.text}"
    # )
    # if response.status_code == 200:
    assert response.status_code == 200

    context_data = response.json()
    assert "provider" in context_data
    assert "max_context_window" in context_data
    assert context_data["provider"] == provider_name
    assert isinstance(context_data["max_context_window"], int)

    # Get expected context window from environment or use default
    expected_window = int(os.getenv("EXPECTED_CONTEXT_WINDOW", "2048"))
    assert context_data["max_context_window"] == expected_window
