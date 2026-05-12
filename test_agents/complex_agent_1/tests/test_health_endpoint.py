import os
import time

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.mark.depends(name="healthy")
def test_health_endpoint():
    """Test the /health endpoint with retries until the service is ready."""
    url = f"{BASE_URL}/health"
    start = time.time()
    timeout = 20
    while True:
        try:
            response = requests.get(url)
            if (
                response.status_code == 200
                and response.json().get("status") == "ok"
            ):
                break
        except Exception:
            pass
        if time.time() - start > timeout:
            raise TimeoutError(
                f"/health did not return status=ok within {timeout} seconds"
            )
        time.sleep(1)
