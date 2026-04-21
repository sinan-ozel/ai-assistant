"""Test health endpoint availability for coding agent."""

import os

import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


def test_health_endpoint():
    """Test the health endpoint returns expected response."""
    url = f"{BASE_URL}/health"
    response = requests.get(url, timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
