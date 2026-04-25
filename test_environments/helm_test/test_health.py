import os

import requests

BASE_URL = os.environ.get("BASE_URL", "http://host.docker.internal:8000")
STREAMLIT_URL = os.environ.get("STREAMLIT_URL", "http://host.docker.internal:8501")


def test_health_endpoint():
    resp = requests.get(f"{BASE_URL}/health", timeout=15)
    assert resp.status_code == 200, f"/health returned {resp.status_code}: {resp.text}"


def test_health_not_loading():
    resp = requests.get(f"{BASE_URL}/health", timeout=15)
    assert resp.status_code == 200, f"/health returned {resp.status_code}: {resp.text}"
    body = resp.json()
    assert body.get("status") == "ok", f"Providers still loading after startup: {body}"


def test_streamlit_up():
    resp = requests.get(STREAMLIT_URL, timeout=15)
    assert resp.status_code == 200, (
        f"Streamlit at {STREAMLIT_URL} returned {resp.status_code}"
    )
