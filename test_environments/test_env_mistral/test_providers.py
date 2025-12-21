import pytest
import requests
import time
import os


BASE_URL = os.getenv("BASE_URL", "http://app:8000")


def test_providers(mistral_api_key_available):
    """Test if the Mistral provider is being discovered correctly."""
    url = f"{BASE_URL}/private/v1/providers"
    start = time.time()
    timeout = 5  # seconds
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200 and response.json().get("status", "") == "multiple_providers_available":
                break
        except Exception:
            pass
        if time.time() - start > timeout:
            break
        time.sleep(1)
    assert response.status_code == 200, f"/private/v1/providers endpoint did not return expected response within {timeout} seconds"
    data = response.json()
    assert data["status"] == "multiple_providers_available"
    assert "available" in data
    assert "default" in data
    assert "total" in data
    assert len(data["available"]) == 1
    assert "pixtral" in data["available"]
    assert data["default"] == "pixtral"


def test_provider_context_window(mistral_api_key_available):
    """Test if the provider's context window endpoint works correctly."""
    # First get the list of providers
    providers_url = f"{BASE_URL}/private/v1/providers"
    response = requests.get(providers_url)
    assert response.status_code == 200
    data = response.json()

    # Get the default provider (should be pixtral)
    provider_name = data["default"]
    assert provider_name == "pixtral"

    # Query the context window endpoint
    context_url = f"{BASE_URL}/private/v1/providers/{provider_name}/max-context-window"
    response = requests.get(context_url)
    assert response.status_code == 200

    context_data = response.json()
    assert "provider" in context_data
    assert "max_context_window" in context_data
    assert context_data["provider"] == "pixtral"
    assert isinstance(context_data["max_context_window"], int)
    assert context_data["max_context_window"] == 4096
