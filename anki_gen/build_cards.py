from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Optional

from .csv_input import iter_csv_rows
from .text_gen import generate_text_data
from .image_gen import generate_image
from .audio_gen import generate_audio
from .anki_tsv import init_tsv, append_anki_row
from .utils import slugify, normalize_tags
from .config import load_config


def main() -> None:
    """
    Entry point for the CLI tool that generates Anki cards (TSV + media).
    """
    parser = argparse.ArgumentParser(
        description="Generate Anki TSV + media for English vocab/grammar using OpenRouter (text+image) and OpenAI TTS."
    )
    parser.add_argument("csv", help="Input CSV file with columns: type,term[,tags]")
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory for anki_cards.tsv and media/ (default: current dir)",
    )
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Skip audio generation (no OpenAI TTS).",
    )
    parser.add_argument(
        "--no-image",
        action="store_true",
        help="Skip image generation.",
    )
    parser.add_argument(
        "--use-silence",
        action="store_true",
        help="In AudioCombined field insert silence between clips. "
             "The silence clip filename is taken from config audio.silence_filename "
             "and must be placed manually into the media directory.",
    )
    parser.add_argument(
        "--tags",
        default="",
        help='Space-separated global tags, e.g. "autogen::2025-11-25 en::vocab".',
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to YAML config (default: config.yaml in project root, or ANKI_GEN_CONFIG env).",
    )

    args = parser.parse_args()

    # Load config before anything else.
    cfg = load_config(args.config)

    csv_path = Path(args.csv)
    if not csv_path.is_file():
        print(f"ERROR: CSV file not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    media_dir = out_dir / "media"
    media_dir.mkdir(parents=True, exist_ok=True)

    tsv_path = out_dir / "anki_cards.tsv"
    init_tsv(tsv_path)

    # Default tags from config + extra tags from CLI.
    cfg_anki = cfg.get("anki", {})
    default_tags = cfg_anki.get("default_tags", []) or []
    cli_tags = [t for t in args.tags.split() if t.strip()]
    global_tags: List[str] = list(default_tags) + cli_tags

    rows = list(iter_csv_rows(csv_path))
    total = len(rows)
    print(f"Processing {total} rows from {csv_path} ...")

    for idx, t, term, row_tags in rows:
        mode = t.strip().lower()
        if mode not in ("word", "rule"):
            print(f"[{idx}] Skipping term '{term}': unknown type '{t}' (use 'word' or 'rule')", file=sys.stderr)
            continue

        slug = slugify(term)
        note_tags = normalize_tags(row_tags, global_tags)

        print(f"\n[{idx}/{total}] {mode.upper()} :: {term} (slug={slug}) tags='{note_tags}'")

        try:
            print("  * Generating text...")
            data = generate_text_data(term, mode)
            definition = data["definition"]
            example = data["example"]

            if not definition:
                print("    WARNING: empty definition", file=sys.stderr)
            if not example:
                print("    WARNING: empty example", file=sys.stderr)

            image_filename: Optional[str] = None
            if not args.no_image:
                print("  * Generating image...")
                image_filename = generate_image(term, mode, media_dir)
                if image_filename:
                    print(f"    Image saved as {image_filename}")

            audio: Dict[str, Optional[str]] = {"term": None, "definition": None, "example": None}
            if not args.no_audio:
                print("  * Generating audio (OpenAI TTS)...")
                audio = generate_audio(term, definition, example, slug, media_dir)
            else:
                print("  * Audio generation skipped (--no-audio)")

            print("  * Writing TSV row...")
            append_anki_row(
                tsv_path,
                term,
                definition,
                example,
                image_filename,
                audio,
                use_silence=args.use_silence,
                tags=note_tags,
            )

        except Exception as e:
            print(f"ERROR processing term '{term}': {e}", file=sys.stderr)
            continue

    print("\nDone.")
    print(f"  TSV:   {tsv_path}")
    print(f"  media: {media_dir}")
    print("Import anki_cards.tsv into Anki as tab-separated UTF-8 and map fields appropriately.")

