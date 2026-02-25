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
                if (
                    status != "initializing"
                    and status == "one_provider_available"
                ):
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
    assert len(data["available"]) >= 2
