from __future__ import annotations

import json
import sys
from typing import Dict

from .openrouter_client import openrouter_chat
from .config import get_config


def extract_json_block(text: str) -> str:
    """
    Extract a JSON object substring from a text response.

    This is a simple heuristic: it looks for the first '{' and the last '}'.
    """
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return text


def generate_text_data(term: str, mode: str) -> Dict[str, str]:
    """
    Generate definition and example sentence for a given term.

    Args:
        term: The vocabulary word or grammar rule name.
        mode: Either "word" or "rule".

    Returns:
        A dict with keys:
            - "definition": short English explanation
            - "example": one example sentence in English
    """
    cfg = get_config()
    text_model = cfg["openrouter"]["text_model"]
    prompts = cfg["prompts"]
    system_prompt = prompts["text_system"]
    templates = prompts["text_user_templates"]

    if mode not in ("word", "rule"):
        raise ValueError(f"Unsupported mode: {mode}")

    user_template = templates[mode]
    user_prompt = user_template.format(term=term)

    resp = openrouter_chat(
        text_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = resp["choices"][0]["message"]["content"]
    json_str = extract_json_block(content)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        print(f"WARNING: could not parse JSON for term '{term}', using raw content as definition", file=sys.stderr)
        data = {
            "definition": content.strip(),
            "example": "",
        }

    for key in ("definition", "example"):
        data.setdefault(key, "")

    return {
        "definition": str(data["definition"]).strip(),
        "example": str(data["example"]).strip(),
    }

