"""Tests for the summarize-text workflow endpoint."""

import json
import os

import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


def test_summarize_text_endpoint():
    """Ensure the /v1/summarize-text endpoint returns a short string
    summary."""
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


def test_summarize_text_streaming_sse():
    """Test the /v1/summarize-text endpoint with SSE streaming."""
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
            "stream": True,
            "stream_format": "sse",
        },
        timeout=10,
        stream=True,
    )

    assert response.status_code == 200
    assert (
        response.headers.get("content-type")
        == "text/event-stream; charset=utf-8"
    )

    chunks = []
    content_parts = []
    done_received = False

    for line in response.iter_lines(decode_unicode=True):
        if line:
            if line.startswith("data: "):
                data = line[6:]  # Remove "data: " prefix
                if data == "[DONE]":
                    done_received = True
                else:
                    chunk = json.loads(data)
                    chunks.append(chunk)
                    # Extract content from delta
                    if "delta" in chunk and "content" in chunk["delta"]:
                        content_parts.append(chunk["delta"]["content"])

    assert len(chunks) > 0, "Expected at least one chunk"
    assert done_received, "Expected [DONE] message"

    # Verify we got content
    full_content = "".join(content_parts)
    assert len(full_content) > 0, "Expected content in streaming response"
    assert len(full_content) < 200, "Summary should be concise"


def test_summarize_text_streaming_ndjson():
    """Test the /v1/summarize-text endpoint with NDJSON streaming."""
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
            "stream": True,
            "stream_format": "ndjson",
        },
        timeout=10,
        stream=True,
    )

    assert response.status_code == 200
    assert "application/x-ndjson" in response.headers.get("content-type", "")

    chunks = []
    content_parts = []
    done_received = False

    for line in response.iter_lines(decode_unicode=True):
        if line:
            chunk = json.loads(line)
            if chunk.get("done"):
                done_received = True
            else:
                chunks.append(chunk)
                # Extract content from delta
                if "delta" in chunk and "content" in chunk["delta"]:
                    content_parts.append(chunk["delta"]["content"])

    assert len(chunks) > 0, "Expected at least one chunk"
    assert done_received, "Expected done message"

    # Verify we got content
    full_content = "".join(content_parts)
    assert len(full_content) > 0, "Expected content in streaming response"
    assert len(full_content) < 200, "Summary should be concise"
