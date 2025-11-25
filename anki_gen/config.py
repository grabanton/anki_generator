from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

# Default configuration used if there is no config.yaml.
_DEFAULT_CONFIG: Dict[str, Any] = {
    "openrouter": {
        "text_model": "google/gemini-2.5-pro",
        "image_model": "google/gemini-2.5-flash-image-preview",
    },
    "openai_tts": {
        "enabled": True,
        "model": "gpt-4o-mini-tts",
        "voice": "alloy",
    },
    "prompts": {
        "text_system": (
            "You are an assistant helping an intermediate English learner.\n"
            "Always reply ONLY with a single valid JSON object. No explanations.\n"
            "Schema:\n"
            "{\n"
            '  \"definition\": \"simple explanation in English, 1-2 short sentences\",\n'
            '  \"example\": \"one natural example sentence in English using the term\"\n'
            "}\n"
            "Use simple, clear language. Avoid rare words."
        ),
        "text_user_templates": {
            "word": (
                'Create an Anki flashcard entry for the English vocabulary word "{term}". '
                "Return JSON exactly in the schema (definition + example)."
            ),
            "rule": (
                'Create an Anki flashcard entry for the English grammar rule "{term}". '
                "Return JSON exactly in the schema (definition + example)."
            ),
        },
        "image_templates": {
            "word": (
                'Create a simple, memorable illustration to help remember the English word "{term}". '
                "Use a clear, iconic visual metaphor. Do not include any text in the image."
            ),
            "rule": (
                'Create a simple, memorable illustration to help remember the English grammar rule "{term}". '
                "Use a clear, iconic visual metaphor. Do not include any text in the image."
            ),
        },
    },
    "image": {
        "aspect_ratio": "1:1",
    },
    "anki": {
        "default_tags": [],
    },
    "audio": {
        "silence_filename": "silence.mp3",
    },
}

_CONFIG: Dict[str, Any] = dict(_DEFAULT_CONFIG)


def _deep_update(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively update mapping `base` with values from `updates`."""
    for k, v in updates.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_update(base[k], v)
        else:
            base[k] = v
    return base


def load_config(path: Optional[str | Path] = None) -> Dict[str, Any]:
    """
    Load YAML configuration and merge it with defaults.

    Priority:
      1. Built-in defaults.
      2. config.yaml in project root (next to build_anki_cards.py).
      3. Explicit file path passed as argument or via ANKI_GEN_CONFIG env var.
    """
    global _CONFIG

    cfg: Dict[str, Any] = {}
    _deep_update(cfg, _DEFAULT_CONFIG)

    # 1. config.yaml in project root
    default_path = Path(__file__).resolve().parent.parent / "config.yaml"
    if default_path.is_file():
        with default_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        _deep_update(cfg, data)

    # 2. override via argument or env
    override_path: Optional[Path] = None
    env_path = os.getenv("ANKI_GEN_CONFIG")
    if path is not None:
        override_path = Path(path)
    elif env_path:
        override_path = Path(env_path)

    if override_path is not None and override_path.is_file():
        with override_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        _deep_update(cfg, data)
    elif override_path is not None and not override_path.is_file():
        print(f"WARNING: config file not found: {override_path}", file=sys.stderr)

    _CONFIG = cfg
    return _CONFIG


def get_config() -> Dict[str, Any]:
    """Return the currently loaded configuration dictionary."""
    return _CONFIG

