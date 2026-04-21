"""Test provider discovery for incorrect_agent."""

import os
import time

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.mark.depends(on=["test_health_endpoint.py::test_health_endpoint"])
def test_providers():
    """Test if the bad_vision provider is being discovered correctly."""
    url = f"{BASE_URL}/private/v1/providers"
    start = time.time()
    timeout = 60  # seconds
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                status = response.json().get("status", "")
                # Wait until discovery completes
                if status != "initializing" and status == "ready":
                    break
        except requests.exceptions.RequestException:
            pass
        if time.time() - start > timeout:
            break
        time.sleep(1)

    assert response.status_code == 200, (
        f"/private/v1/providers endpoint did not return expected response within {timeout} seconds"
    )

    data = response.json()
    print(f"Providers data: {data}")

    assert "available" in data
    assert "bad_vision" in data["available"], (
        f"Expected 'bad_vision' to be in available providers but got {data['available']}"
    )
    assert "default" in data
    assert data["default"] == "bad_vision", (
        f"Expected default provider to be 'bad_vision' but got '{data['default']}'"
    )
