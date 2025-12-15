import requests
import time
import os


BASE_URL = os.getenv("BASE_URL", "http://app:8000")


def test_health_endpoint():
    """Test the /health endpoint with retries and timeout."""
    url = f"{BASE_URL}/health"
    start = time.time()
    timeout = 20  # seconds
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200 and response.json() == {"status": "ok"}:
                break
        except Exception:
            pass
        if time.time() - start > timeout:
            raise TimeoutError(f"/health endpoint did not return expected response within {timeout} seconds")
        time.sleep(1)
