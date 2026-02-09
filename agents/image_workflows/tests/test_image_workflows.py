"""Tests for image-based workflow endpoints."""
import base64
import os
import requests
from pathlib import Path


def get_image_base64(image_path: Path) -> str:
    """Convert image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Hardcoded path to test images directory (replace fixture)
IMAGES_DIR = Path(__file__).parent / "images"


BASE_URL = os.getenv("BASE_URL", "http://app:8000")


def test_nutrition_information_extraction():
    """Test nutrition information extraction from food label image."""
    image_path = IMAGES_DIR / "IMG_B768CE83-9FEC-461A-BE63-CDDF64EBEB58.jpeg"
    image_base64 = get_image_base64(image_path)
    url = f"{BASE_URL}/v1/extract-nutrition-information"

    response = requests.post(
        url,
        json={
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                        }
                    ],
                }
            ],
            "temperature": 0.0,
            "max_tokens": 500,
        },
        timeout=300,  # Must be longer than provider timeout (150s) + buffer
    )

    assert response.status_code == 200
    data = response.json()

    print(data)

    assert isinstance(data, dict)
    assert 'result' in data
    result = data['result']

    # User will write final assertions
    # Expected structure: {"calories": int, "serving_size": float, "unit": str}

    assert "calories" in result
    assert "serving_size" in result
    assert "unit" in result
    assert isinstance(result["calories"], int)
    assert isinstance(result["serving_size"], (int, float))
    assert isinstance(result["unit"], str)
    assert result["calories"] == 180
    assert result["serving_size"] == 40.0
    assert result["unit"] == "g"

def test_book_title_extraction_image_0161():
    """Test book title extraction from book cover image (IMG_0161.JPG)."""
    image_path = IMAGES_DIR / "IMG_0161.JPG"
    image_base64 = get_image_base64(image_path)
    url = f"{BASE_URL}/v1/extract-book-title"

    response = requests.post(
        url,
        json={
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                        }
                    ],
                }
            ],
            "temperature": 0.0,
            "max_tokens": 100,
        },
        timeout=300,  # Must be longer than provider timeout (150s) + buffer
    )

    assert response.status_code == 200
    data = response.json()

    # User will write final assertions
    # Expected: string containing book title
    assert isinstance(data, dict)
    assert len(data['result']) > 0
    print(data)
    assert data['result'].strip() == 'THE BIG STICK'
