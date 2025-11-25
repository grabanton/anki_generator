from __future__ import annotations

import base64
import sys
from pathlib import Path
from typing import Optional

from .openrouter_client import openrouter_chat
from .utils import slugify
from .config import get_config


def generate_image(term: str, mode: str, media_dir: Path) -> Optional[str]:
    """
    Generate an image for a given term and save it to the media directory.

    Args:
        term: Vocabulary word or grammar rule name.
        mode: "word" or "rule".
        media_dir: Directory where the image file should be written.

    Returns:
        Filename (relative to media_dir) or None on failure.
    """
    cfg = get_config()
    image_model = cfg["openrouter"]["image_model"]
    aspect_ratio = cfg["image"].get("aspect_ratio", "1:1")
    templates = cfg["prompts"]["image_templates"]

    if mode not in ("word", "rule"):
        raise ValueError(f"Unsupported mode: {mode}")

    user_template = templates[mode]
    prompt = user_template.format(term=term)

    resp = openrouter_chat(
        image_model,
        messages=[{"role": "user", "content": prompt}],
        extra={"modalities": ["image", "text"], "image_config": {"aspect_ratio": aspect_ratio}},
    )

    message = resp["choices"][0]["message"]
    images = message.get("images") or []
    if not images:
        print(f"WARNING: no images in response for '{term}'", file=sys.stderr)
        return None

    data_url = images[0]["image_url"]["url"]
    if "," not in data_url:
        print(f"WARNING: unexpected image URL format for '{term}'", file=sys.stderr)
        return None

    _, b64data = data_url.split(",", 1)
    img_bytes = base64.b64decode(b64data)

    filename = slugify(term) + ".png"
    filepath = media_dir / filename
    with open(filepath, "wb") as f:
        f.write(img_bytes)

    return filename

