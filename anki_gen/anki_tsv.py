from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional, Dict

from .utils import sound_tag, build_audio_combined


def init_tsv(tsv_path: Path) -> None:
    """
    Initialize the TSV file with a header row if it does not yet exist.
    """
    if tsv_path.exists():
        return
    with tsv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow([
            "Term",
            "Definition",
            "Example",
            "ImageHTML",
            "AudioTerm",
            "AudioDefinition",
            "AudioExample",
            "AudioCombined",
            "Tags",
        ])


def append_anki_row(
    tsv_path: Path,
    term: str,
    definition: str,
    example: str,
    image_filename: Optional[str],
    audio: Dict[str, Optional[str]],
    use_silence: bool,
    tags: str,
) -> None:
    """
    Append a single note row to the TSV file.

    Columns:
        Term, Definition, Example, ImageHTML,
        AudioTerm, AudioDefinition, AudioExample,
        AudioCombined, Tags
    """
    image_html = f'<img src="{image_filename}">' if image_filename else ""

    row = [
        term,
        definition,
        example,
        image_html,
        sound_tag(audio.get("term")),
        sound_tag(audio.get("definition")),
        sound_tag(audio.get("example")),
        build_audio_combined(audio, use_silence),
        tags,
    ]

    with tsv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(row)

