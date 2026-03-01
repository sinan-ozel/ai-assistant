"""Pytest configuration and fixtures for image workflow tests."""

import os

import pytest

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.fixture(scope="function")
def clear_evaluation_state():
    """Clear Redis evaluation state before running evaluation tests.

    This fixture runs before each test to ensure a clean state
    for evaluation tests, preventing old state from interfering.
    """
    try:
        # Import redis_memory to clear the evaluation state
        # Note: This runs in the test container, which needs redis_memory installed
        import redis

        # Connect to Redis (same connection redis_memory uses)
        redis_host = os.getenv("REDIS_HOST", "redis")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))

        r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

        # Delete the workflow_evaluation_state key
        # redis_memory stores data with a "memory:" namespace prefix by default
        r.delete("memory:workflow_evaluation_state")

        print("\n✅ Cleared Redis evaluation state")
    except Exception as e:
        # If Redis isn't available or there's an error, just warn but don't fail
        print(f"\n⚠️  Warning: Could not clear Redis evaluation state: {e}")

    yield

    # Optional: Could also clear after tests if needed
    # try:
    #     r.delete("evaluation:workflow_evaluation_state")
    # except:
    #     pass


# @pytest.fixture(scope="session")
# def api_client():
#     """Create a requests session configured for the API."""
#     # Wait for health endpoint first
#     url = f"{BASE_URL}/health"
#     start = time.time()
#     timeout = 20  # seconds
#     while True:
#         try:
#             response = requests.get(url)
#             if response.status_code == 200 and response.json().get("status") == "ok":
#                 break
#         except Exception:
#             pass
#         if time.time() - start > timeout:
#             raise TimeoutError(f"/health endpoint did not return expected response within {timeout} seconds")
#         time.sleep(1)

#     # Create session
#     session = requests.Session()
#     session.headers.update({"Content-Type": "application/json"})

#     class APIClient:
#         def __init__(self, session, base_url):
#             self.session = session
#             self.base_url = base_url

#         def post(self, path, **kwargs):
#             return self.session.post(f"{self.base_url}{path}", **kwargs)

#         def get(self, path, **kwargs):
#             return self.session.get(f"{self.base_url}{path}", **kwargs)

#     return APIClient(session, BASE_URL)
