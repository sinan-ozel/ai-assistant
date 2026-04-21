"""Tests for max_tokens edge cases in workflow endpoints.

These tests probe how the nutrition extraction endpoint behaves when
max_tokens is too low (should fail with a clear error), very large,
or omitted entirely.
"""

import base64
import json
import os
from pathlib import Path

import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")
IMAGES_DIR = Path(__file__).parent / "images"
IMAGE_PATH = IMAGES_DIR / "IMG_B768CE83-9FEC-461A-BE63-CDDF64EBEB58.jpeg"
URL = f"{BASE_URL}/v1/extract-nutrition-information"


def get_image_base64(image_path: Path) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _image_message(image_base64: str) -> dict:
    return {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
            }
        ],
    }


def test_nutrition_extraction_low_max_tokens():
    """With max_tokens=50, a reasoning model exhausts the budget before
    producing any output. The endpoint should return 400 and the error
    message should hint that max_tokens may be too low."""
    image_base64 = get_image_base64(IMAGE_PATH)

    response = requests.post(
        URL,
        json={
            "messages": [_image_message(image_base64)],
            "temperature": 0.0,
            "max_tokens": 50,
        },
        timeout=300,
    )

    assert response.status_code == 400, (
        f"Expected 400 but got {response.status_code}: {response.content}"
    )
    detail = response.json().get("detail", {})
    error = detail.get("error", "") if isinstance(detail, dict) else str(detail)
    assert "max_tokens" in error.lower(), (
        f"Expected max_tokens hint in error message, got: {error!r}"
    )


def test_nutrition_extraction_streaming_ndjson_low_max_tokens():
    """Same as above but via the NDJSON streaming path.

    With max_tokens=50, the model produces no visible content.
    The final streaming chunk should carry a parse_error that mentions
    max_tokens."""
    image_base64 = get_image_base64(IMAGE_PATH)

    response = requests.post(
        URL,
        json={
            "messages": [_image_message(image_base64)],
            "temperature": 0.0,
            "max_tokens": 50,
            "stream": True,
            "stream_format": "ndjson",
        },
        timeout=300,
        stream=True,
    )

    assert response.status_code == 200, (
        f"Streaming endpoint returned {response.status_code}: {response.content}"
    )

    chunks = []
    for line in response.iter_lines(decode_unicode=True):
        if line:
            chunks.append(json.loads(line))

    assert len(chunks) > 0, "Expected at least one chunk"

    # Find the chunk that carries the error or the done sentinel
    error_chunk = next(
        (c for c in chunks if "parse_error" in c or "error" in c), None
    )
    assert error_chunk is not None, (
        f"Expected a chunk with parse_error or error, got: {chunks}"
    )
    error_text = error_chunk.get("parse_error", "") or str(
        error_chunk.get("error", "")
    )
    assert "max_tokens" in error_text.lower(), (
        f"Expected max_tokens hint in parse_error, got: {error_text!r}"
    )


def test_nutrition_extraction_large_max_tokens():
    """Test behaviour when max_tokens is very large (128 * 1024).

    This test always fails intentionally so the response can be inspected.
    """
    image_base64 = get_image_base64(IMAGE_PATH)

    response = requests.post(
        URL,
        json={
            "messages": [_image_message(image_base64)],
            "temperature": 0.0,
            "max_tokens": 128 * 1024,
        },
        timeout=300,
    )

    print(response.content)
    assert response.status_code == 200, f"status={response.status_code}"
    data = response.json()

    assert isinstance(data, dict)
    assert len(data["result"]) > 0
    print(data)
    assert 'calories' in data['result']


def test_nutrition_extraction_no_max_tokens():
    """Explore behaviour when max_tokens is omitted entirely.

    This test always fails intentionally so the response can be inspected.
    """
    image_base64 = get_image_base64(IMAGE_PATH)

    response = requests.post(
        URL,
        json={
            "messages": [_image_message(image_base64)],
            "temperature": 0.0,
        },
        timeout=300,
    )

    print(response.content)
    assert response.status_code == 200, f"status={response.status_code}"
    data = response.json()

    assert isinstance(data, dict)
    assert len(data["result"]) > 0
    print(data)
    assert 'calories' in data['result']
    assert 'usage' in data
    assert 'completion_tokens' in data['usage']
    assert isinstance(data['usage']['completion_tokens'], int)
