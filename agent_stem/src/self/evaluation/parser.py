"""Evaluation case parser.

Parses evaluation YAML configuration from workflow definitions.
"""

import base64
import io
from pathlib import Path
from typing import Any, Dict, List

import yaml
from PIL import Image


def convert_image_to_jpeg_base64(image_path: Path, quality: int = 60) -> str:
    """Open an image, resize so the larger dimension is 512px (max), convert to
    RGB if needed, encode as JPEG, and return base64 data URL."""
    img = Image.open(image_path)

    if img.mode != "RGB":
        img = img.convert("RGB")

    # Resize proportionally (max width/height = 512)
    max_size = (512, 512)
    img.thumbnail(max_size, Image.LANCZOS)

    # Encode to JPEG in memory
    img_bytes_io = io.BytesIO()
    img.save(img_bytes_io, format="JPEG", quality=quality, optimize=True)
    img_bytes_io.seek(0)

    b64 = base64.b64encode(img_bytes_io.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


def parse_evaluation_yaml(
    evaluation_yaml_str: str, base_dir: Path
) -> List[Dict[str, Any]]:
    """Parse evaluation configuration from YAML string.

    Args:
        evaluation_yaml_str: YAML string containing evaluation configuration
        base_dir: Base directory for resolving relative paths (e.g., image paths)

    Returns:
        List of parsed test cases

    Raises:
        ValueError: If YAML is invalid or missing required fields
        FileNotFoundError: If referenced files are not found
    """
    try:
        data = yaml.safe_load(evaluation_yaml_str)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML: {e}")

    if not data:
        raise ValueError("Empty evaluation configuration")

    # Extract top-level defaults
    top_level_prompt = data.get("prompt")
    top_level_prompt_path = data.get("prompt_path")
    if top_level_prompt and top_level_prompt_path:
        raise ValueError(
            "Cannot have both 'prompt' and 'prompt_path'. "
            "Either write the prompt into the YAML file or provide a prompt file path."
        )

    top_level_repeat = data.get("repeat")
    top_level_threshold = data.get("threshold")

    all_tests = []
    for test in data.get("cases", []):
        test_id = test.get("id")
        repeat = test.get("repeat", top_level_repeat)
        threshold = test.get("threshold", top_level_threshold)
        steps = test.get("steps", [])

        if not test_id:
            raise ValueError("Every test must have an 'id'.")
        if not steps:
            raise ValueError(
                f"Test '{test_id}' must contain at least one step."
            )

        parsed_steps = []
        for idx, step in enumerate(steps):
            step_content = []
            inp = step.get("input", {})
            prompt = inp.get("prompt") or top_level_prompt
            prompt_path = inp.get("prompt_path") or top_level_prompt_path
            img_path = inp.get("image_path")
            max_tokens = (
                int(inp.get("max_tokens"))
                if inp.get("max_tokens") is not None
                else None
            )

            if not (prompt or prompt_path) and not img_path:
                raise ValueError(
                    f"Test '{test_id}', step {idx}: need text or image."
                )

            if (prompt and not top_level_prompt) and (
                prompt_path and not top_level_prompt_path
            ):
                raise ValueError(
                    f"Test '{test_id}', step {idx}: cannot have both"
                    " 'prompt' and 'prompt_path'. Either write the prompt"
                    " into the YAML file or provide a prompt file path."
                )

            if prompt_path and not prompt_path.endswith(".md"):
                raise ValueError(
                    f"Test '{test_id}', step {idx}: prompt_path must"
                    " point to a .md file."
                )

            image_url = None
            if img_path:
                # Resolve image path relative to the base directory
                p = base_dir / Path(img_path)
                if not p.exists():
                    raise FileNotFoundError(
                        f"Image not found: {img_path} (resolved to {p})"
                    )

                image_url = convert_image_to_jpeg_base64(p, quality=60)

            if prompt:
                step_content.append({"type": "text", "text": prompt})

            if prompt_path:
                prompt_file = base_dir / Path(prompt_path)
                if not prompt_file.exists():
                    raise FileNotFoundError(
                        f"Prompt file not found: {prompt_path}"
                    )
                prompt_text = prompt_file.read_text()
                step_content.append({"type": "text", "text": prompt_text})

            if image_url:
                step_content.append(
                    {"type": "image_url", "image_url": {"url": image_url}}
                )

            expectations = step.get("expectations", [])
            parsed_steps.append(
                {
                    "content": step_content,
                    "max_tokens": max_tokens,
                    "expectations": expectations,
                }
            )

        all_tests.append(
            {
                "id": test_id,
                "repeat": repeat,
                "threshold": threshold,
                "steps": parsed_steps,
            }
        )

    return all_tests
