from __future__ import annotations

import re
from typing import Optional, Dict, List

from .config import get_config


def slugify(text: str) -> str:
    """Convert arbitrary text to a filesystem-friendly slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = text.strip("_")
    return text or "term"


def sound_tag(filename: Optional[str]) -> str:
    """Return an Anki sound tag for a given filename, or an empty string."""
    if not filename:
        return ""
    return f"[sound:{filename}]"


def build_audio_combined(audio: Dict[str, Optional[str]], use_silence: bool) -> str:
    """
    Build a combined audio field for Anki.

    Order:
        term, (silence), definition, (silence), example

    If use_silence = True, inserts a silence clip between segments using
    the filename from config audio.silence_filename.
    """
    cfg = get_config()
    silence_name = cfg.get("audio", {}).get("silence_filename", "silence.mp3")

    parts: List[str] = []
    if audio.get("term"):
        parts.append(sound_tag(audio["term"]))
    if use_silence:
        parts.append(sound_tag(silence_name))
    if audio.get("definition"):
        parts.append(sound_tag(audio["definition"]))
    if use_silence:
        parts.append(sound_tag(silence_name))
    if audio.get("example"):
        parts.append(sound_tag(audio["example"]))
    return "".join(parts)


def normalize_tags(row_tags: str, global_tags: List[str]) -> str:
    """
    Merge tags from the CSV row and global CLI/config tags.

    Tags are space-separated strings. Duplicates are removed while preserving order.
    """
    tags: List[str] = []
    if row_tags:
        tags.extend(t for t in row_tags.split() if t.strip())
    tags.extend(global_tags)
    seen = set()
    uniq: List[str] = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return " ".join(uniq)

