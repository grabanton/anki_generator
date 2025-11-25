from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional, Dict

import requests

from .config import get_config

OPENAI_TTS_URL = "https://api.openai.com/v1/audio/speech"


def tts_one_clip(text: str, filename: str, media_dir: Path) -> Optional[str]:
    """
    Synthesize a single audio clip using OpenAI TTS.

    Args:
        text: Text to be spoken.
        filename: Output filename (relative to media_dir).
        media_dir: Directory to store the audio file.

    Returns:
        The filename if TTS succeeded, or None if skipped.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    cfg = get_config()
    tts_cfg = cfg.get("openai_tts", {})
    model = tts_cfg.get("model", "gpt-4o-mini-tts")
    voice = tts_cfg.get("voice", "alloy")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "voice": voice,
        "format": "mp3",
        "input": text,
    }

    resp = requests.post(OPENAI_TTS_URL, headers=headers, json=payload, timeout=180)
    resp.raise_for_status()

    audio_bytes = resp.content
    path = media_dir / filename
    with open(path, "wb") as f:
        f.write(audio_bytes)

    return filename


def generate_audio(term: str, definition: str, example: str, slug: str, media_dir: Path) -> Dict[str, Optional[str]]:
    """
    Generate audio files for term, definition, and example.

    Args:
        term: Vocabulary word or grammar rule name.
        definition: Short English explanation.
        example: Example sentence in English.
        slug: Base filename slug.
        media_dir: Directory to store the audio files.

    Returns:
        Dict with keys "term", "definition", "example" mapping to filenames or None.
    """
    audio: Dict[str, Optional[str]] = {
        "term": None,
        "definition": None,
        "example": None,
    }

    cfg = get_config()
    tts_cfg = cfg.get("openai_tts", {})
    if not tts_cfg.get("enabled", True):
        print("NOTE: TTS disabled in config (openai_tts.enabled = false)", file=sys.stderr)
        return audio

    if not os.getenv("OPENAI_API_KEY"):
        print("NOTE: OPENAI_API_KEY not set, skipping audio generation", file=sys.stderr)
        return audio

    audio["term"] = tts_one_clip(term, slug + "_term.mp3", media_dir)
    audio["definition"] = tts_one_clip(definition, slug + "_def.mp3", media_dir)
    audio["example"] = tts_one_clip(example, slug + "_ex.mp3", media_dir)

    return audio

