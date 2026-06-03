"""Tests for image input via the agent chat endpoint.

Verifies that the `media` field on POST /v1/agent/chat correctly forwards
base64-encoded images to the LLM and returns a coherent response.
"""

import base64
import os
from pathlib import Path

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")
IMAGES_DIR = Path(__file__).parent / "images"


def _b64(image_path: Path) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _skip_if_no_vision(response: requests.Response) -> None:
    """Skip the test if the model doesn't support image input."""
    if response.status_code == 422:
        detail = response.json().get("detail", "")
        if "image" in detail.lower() or "vision" in detail.lower():
            pytest.skip("Model does not support image input")


@pytest.mark.depends(on="healthy")
def test_agent_chat_with_jpeg_image():
    """Agent responds when an image is attached via the media field."""
    image_b64 = _b64(IMAGES_DIR / "IMG_0161.JPG")

    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "Describe what you see in this image in one sentence.",
            "user_id": "test-image-media-1",
            "media": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_b64}"
                    },
                }
            ],
        },
        timeout=300,
    )

    _skip_if_no_vision(response)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "conversation_id" in data
    assert "message" in data
    assert data["role"] == "assistant"
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


def test_agent_chat_media_without_text_message_is_rejected():
    """Empty message string is rejected even when media is present."""
    image_b64 = _b64(IMAGES_DIR / "IMG_0161.JPG")

    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "",
            "user_id": "test-image-media-2",
            "media": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_b64}"
                    },
                }
            ],
        },
        timeout=30,
    )

    assert response.status_code == 400


@pytest.mark.depends(on="test_agent_chat_with_jpeg_image")
def test_agent_chat_multiple_images():
    """Agent accepts multiple images in a single request."""
    image_b64_1 = _b64(IMAGES_DIR / "IMG_0161.JPG")
    image_b64_2 = _b64(IMAGES_DIR / "IMG_0166.JPG")

    response = requests.post(
        f"{BASE_URL}/v1/agent/chat",
        json={
            "message": "How many images did I send you?",
            "user_id": "test-image-media-3",
            "media": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_b64_1}"
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_b64_2}"
                    },
                },
            ],
        },
        timeout=300,
    )

    _skip_if_no_vision(response)
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0
