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
    def format_img_tag(filename: Optional[str]) -> str:
        return f'<img src="{filename}" style="max-with: 150px; height: auto">' if filename else ""

    def format_sound(filename: Optional[str]) -> str:
        return sound_tag(filename)

    row = [
        term,
        definition,
        example,
        format_img_tag(image_filename),
        format_sound(audio.get("term")),
        format_sound(audio.get("definition")),
        format_sound(audio.get("example")),
        tags,
    ]

    with tsv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(row)

