#!/usr/bin/env python3
"""Render selected pages from the immutable source examination for local review."""

from __future__ import annotations

import argparse
from pathlib import Path

import pymupdf


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", nargs="+", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scale", type=float, default=2.0)
    args = parser.parse_args()

    source = ROOT / "แนวข้อสอบ.pdf"
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    destination.mkdir(parents=True, exist_ok=True)
    document = pymupdf.open(source)
    for page_number in args.pages:
        if not 1 <= page_number <= document.page_count:
            raise SystemExit(f"page {page_number} outside 1–{document.page_count}")
        page = document[page_number - 1]
        pixmap = page.get_pixmap(
            matrix=pymupdf.Matrix(args.scale, args.scale),
            alpha=False,
        )
        output = destination / f"exam-page-{page_number:02d}.png"
        pixmap.save(output)
        print(output.relative_to(ROOT) if output.is_relative_to(ROOT) else output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
