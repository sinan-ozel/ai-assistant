"""Tests for image vision via the chat completions endpoint."""

import base64
import os
from pathlib import Path

import requests

import pytest

BASE_URL = os.getenv("BASE_URL", "http://app:8000")

IMAGES_DIR = Path(__file__).parent / "images"


def get_image_data_url(image_path: Path) -> str:
    """Encode an image file as a base64 data URL."""
    suffix = image_path.suffix.lower()
    mime_type = "image/jpeg" if suffix in {".jpg", ".jpeg"} else "image/png"
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


@pytest.mark.depends(on=["healthy"])
def test_chat_completions_describes_image():
    """Test that the vision model describes the contents of IMG_0161.JPG."""
    image_path = IMAGES_DIR / "IMG_0161.JPG"
    data_url = get_image_data_url(image_path)

    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        json={
            "model": "vision",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url},
                        },
                        {
                            "type": "text",
                            "text": "What is in this image? Please describe what you see.",
                        },
                    ],
                }
            ],
            "max_tokens": 256,
            "temperature": 0.0,
        },
        timeout=300,
    )

    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()

    assert "choices" in data
    assert len(data["choices"]) > 0
    content = data["choices"][0]["message"]["content"]
    assert isinstance(content, str)
    assert len(content) > 0
    assert (
        "stick" in content.lower()
    ), "Expected to see 'stick' in content, got: {content}"


@pytest.mark.depends(on=["healthy"])
def test_chat_completions_image_response_structure():
    """Test that the vision chat response has the expected OpenAI structure."""
    image_path = IMAGES_DIR / "IMG_0161.JPG"
    data_url = get_image_data_url(image_path)

    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        json={
            "model": "vision",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url},
                        },
                        {
                            "type": "text",
                            "text": "What is in this image? Please describe what you see.",
                        },
                    ],
                }
            ],
            "max_tokens": 128,
            "temperature": 0.0,
        },
        timeout=300,
    )

    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert "choices" in data
    assert "usage" in data
    choice = data["choices"][0]
    assert "message" in choice
    assert choice["message"]["role"] == "assistant"
