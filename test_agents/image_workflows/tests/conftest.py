"""Pytest configuration and fixtures for image workflow tests."""

import pytest
import requests
import os
import time

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


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
