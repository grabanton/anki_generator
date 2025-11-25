from __future__ import annotations

import os
import sys
from typing import Optional, Dict, Any, List

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def require_env(name: str) -> str:
    """Return the value of an environment variable or exit with an error."""
    value = os.getenv(name)
    if not value:
        print(f"ERROR: environment variable {name} is not set", file=sys.stderr)
        sys.exit(1)
    return value


def openrouter_chat(model: str, messages: List[Dict[str, Any]], extra: Optional[dict] = None) -> Dict[str, Any]:
    """
    Call the OpenRouter chat completions endpoint.

    Args:
        model: Model name to use.
        messages: Chat messages list.
        extra: Extra JSON fields to merge into the request payload.

    Returns:
        Parsed JSON response from OpenRouter.
    """
    api_key = require_env("OPENROUTER_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://local-tool",
        "X-Title": "anki-vocab-builder",
    }
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
    }
    if extra:
        payload.update(extra)

    resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=180)
    resp.raise_for_status()
    return resp.json()

