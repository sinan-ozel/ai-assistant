import pytest
import requests
import time
import os


BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.mark.depends(on=["test_health_endpoint.py::test_health_endpoint"])
def test_providers():
    """Test if the default providers are being discovered correctly."""
    url = f"{BASE_URL}/private/v1/providers"
    start = time.time()
    timeout = 5  # seconds
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200 and response.json().get("status", "") == "no_providers_available":
                break
        except Exception:
            pass
        if time.time() - start > timeout:
            raise TimeoutError(f"/private/v1/providers endpoint did not return expected response within {timeout} seconds")
        time.sleep(1)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "no_providers_available"
    assert "available" in data
    assert "default" in data
    assert "total" in data
    assert data["available"] == []
