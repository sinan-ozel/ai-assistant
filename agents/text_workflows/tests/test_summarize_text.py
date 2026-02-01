"""Tests for the summarize-text workflow endpoint."""
import os
import requests


BASE_URL = os.getenv("BASE_URL", "http://app:8000")


def test_summarize_text_endpoint():
    """Ensure the /v1/summarize-text endpoint returns a short string summary."""
    url = f"{BASE_URL}/v1/summarize-text"

    response = requests.post(
        url,
        json={
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "This is a long message that needs to be summarized. "
                        "It contains several sentences and should be condensed into a concise summary."
                    ),
                }
            ],
            "temperature": 0.0,
            "max_tokens": 200,
        },
        timeout=10,
    )

    assert response.status_code == 200
    data = response.json()

    # The workflow's output_schema is a plain string, so the response should be
    # an object with a `result` string and a `usage` object.
    assert isinstance(data, dict)
    assert "result" in data
    assert isinstance(data["result"], str)

    # Basic checks on length: should be shorter than the original input
    assert len(data["result"]) > 0
    assert len(data["result"]) < 200
