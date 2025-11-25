from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Iterator, Tuple


def iter_csv_rows(csv_path: Path) -> Iterator[Tuple[int, str, str, str]]:
    """
    Iterate over CSV rows and yield (row_index, type, term, row_tags).

    CSV must have at least the headers: type, term.
    A 'tags' column is optional.
    """
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if "type" not in reader.fieldnames or "term" not in reader.fieldnames:
            print("ERROR: CSV must have headers at least: type,term", file=sys.stderr)
            sys.exit(1)

        has_tags_column = "tags" in reader.fieldnames

        for i, row in enumerate(reader, start=1):
            t = (row.get("type") or "").strip()
            term = (row.get("term") or "").strip()
            if not t or not term:
                print(f"Skipping row {i}: empty type/term", file=sys.stderr)
                continue
            row_tags = (row.get("tags") or "").strip() if has_tags_column else ""
            yield i, t, term, row_tags

