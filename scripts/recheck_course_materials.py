#!/usr/bin/env python3
"""Rank local course-material passages for every non-course-verified question.

The script reads only local files. It is a discovery aid: ranked candidates
must be inspected before any question is classified as course-verified.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SEARCHABLE_CATEGORIES = {
    "course_outline",
    "lecture",
    "other_academic_material",
    "summary",
    "exercise_or_assignment",
}
STOPWORDS = {
    "about", "above", "after", "again", "all", "also", "among", "and",
    "are", "been", "being", "best", "both", "business", "called", "can",
    "company", "consider", "correct", "could", "data", "does", "each",
    "following", "for", "from", "has", "have", "how", "into", "its", "may",
    "most", "not", "one", "only", "other", "should", "system", "than", "that",
    "the", "their", "them", "then", "there", "these", "they", "this", "those",
    "through", "true", "used", "using", "what", "when", "where", "which",
    "with", "would", "your",
}
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")


def xml_text(blob: bytes) -> str:
    root = ElementTree.fromstring(blob)
    return " ".join(
        node.text.strip()
        for node in root.iter()
        if node.text and node.text.strip() and node.tag.rsplit("}", 1)[-1] in {"t", "v", "f", "p"}
    )


def numbered_xml_parts(
    path: Path, pattern: re.Pattern[str], number_pattern: re.Pattern[str]
) -> Iterable[tuple[str, str]]:
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if pattern.search(name)]
        names.sort(
            key=lambda name: int(number_pattern.search(name).group(1))
            if number_pattern.search(name)
            else 0
        )
        for name in names:
            yield name, xml_text(archive.read(name))


def extract_segments(path: Path) -> Iterable[tuple[str, str]]:
    suffix = path.suffix.casefold()
    try:
        if suffix == ".pdf":
            reader = PdfReader(str(path), strict=False)
            if reader.is_encrypted and not reader.decrypt(""):
                return
            for index, page in enumerate(reader.pages, 1):
                yield f"page {index}", page.extract_text() or ""
        elif suffix == ".pptx":
            yield from (
                (f"slide {index}", text)
                for index, (_, text) in enumerate(
                    numbered_xml_parts(
                        path,
                        re.compile(r"ppt/slides/slide\d+\.xml$"),
                        re.compile(r"slide(\d+)\.xml$"),
                    ),
                    1,
                )
            )
        elif suffix == ".docx":
            with zipfile.ZipFile(path) as archive:
                names = [
                    name
                    for name in archive.namelist()
                    if name == "word/document.xml"
                    or name.startswith("word/header")
                    or name.startswith("word/footer")
                ]
                yield "document", " ".join(xml_text(archive.read(name)) for name in names)
        elif suffix == ".xlsx":
            yield from (
                (f"sheet {index}", text)
                for index, (_, text) in enumerate(
                    numbered_xml_parts(
                        path,
                        re.compile(r"xl/worksheets/sheet\d+\.xml$"),
                        re.compile(r"sheet(\d+)\.xml$"),
                    ),
                    1,
                )
            )
        elif suffix in {".doc", ".ppt", ".xls"}:
            converted = subprocess.run(
                ["textutil", "-convert", "txt", "-stdout", str(path)],
                capture_output=True,
                check=False,
            )
            if converted.returncode == 0:
                yield "document", converted.stdout.decode("utf-8", errors="replace")
        elif suffix in {
            ".txt", ".md", ".csv", ".html", ".htm", ".json", ".xml", ".js",
            ".ts", ".tsx", ".jsx", ".php", ".py", ".java", ".css", ".url",
        }:
            yield "document", path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        yield "extraction error", f"[local extraction failed: {type(exc).__name__}: {exc}]"


def tokens(text: str) -> set[str]:
    return {
        token.casefold()
        for token in TOKEN_RE.findall(text)
        if token.casefold() not in STOPWORDS
    }


def compact(text: str) -> str:
    return " ".join(text.split())


def snippet(text: str, matched: set[str], size: int = 620) -> str:
    normalized = compact(text)
    lowered = normalized.casefold()
    positions = [lowered.find(token) for token in matched if lowered.find(token) >= 0]
    start = max(0, (min(positions) if positions else 0) - 120)
    return normalized[start : start + size]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/course-material-recheck-candidates.json"),
    )
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args()

    inventory = json.loads(
        (ROOT / "data/file-inventory.json").read_text(encoding="utf-8")
    )["files"]
    questions = json.loads(
        (ROOT / "data/questions.json").read_text(encoding="utf-8")
    )["questions"]
    cohort = [
        item for item in questions if item["answer_status"] != "verified_from_source"
    ]

    segments: list[dict[str, Any]] = []
    extraction_errors: list[dict[str, str]] = []
    for record in inventory:
        if record["document_category"] not in SEARCHABLE_CATEGORIES:
            continue
        path = ROOT / record["relative_path"]
        for locator, text in extract_segments(path):
            if locator == "extraction error":
                extraction_errors.append(
                    {"relative_path": record["relative_path"], "error": text}
                )
                continue
            normalized = compact(text)
            if not normalized:
                continue
            segments.append(
                {
                    "file_id": record["file_id"],
                    "relative_path": record["relative_path"],
                    "document_category": record["document_category"],
                    "detected_subject_code": record["detected_subject_code"],
                    "locator": locator,
                    "text": normalized,
                    "tokens": tokens(normalized),
                }
            )

    document_frequency: Counter[str] = Counter()
    for segment in segments:
        document_frequency.update(segment["tokens"])
    segment_count = len(segments)

    results: list[dict[str, Any]] = []
    for question in cohort:
        query_text = " ".join(
            [
                question["original_question_en"],
                *(choice["original_text_en"] for choice in question["choices"]),
            ]
        )
        query_tokens = tokens(query_text)
        answer_choice = next(
            (
                choice
                for choice in question["choices"]
                if choice["choice_id"] == question.get("correct_answer")
            ),
            None,
        )
        answer_text = compact(
            answer_choice["original_text_en"] if answer_choice else ""
        )
        answer_tokens = tokens(answer_text)
        candidates: list[dict[str, Any]] = []
        answer_hits: list[dict[str, Any]] = []
        for segment in segments:
            matched = query_tokens & segment["tokens"]
            if len(matched) < 2:
                continue
            score = sum(
                math.log((segment_count + 1) / (document_frequency[token] + 1)) + 1
                for token in matched
            )
            if segment["detected_subject_code"] == question["subject_code"]:
                score *= 1.35
            candidates.append(
                {
                    "file_id": segment["file_id"],
                    "relative_path": segment["relative_path"],
                    "document_category": segment["document_category"],
                    "locator": segment["locator"],
                    "detected_subject_code": segment["detected_subject_code"],
                    "score": round(score, 3),
                    "matched_terms": sorted(matched),
                    "passage": snippet(segment["text"], matched),
                }
            )
            if (
                answer_text
                and (
                    answer_text.casefold() in segment["text"].casefold()
                    or (
                        len(answer_tokens) >= 2
                        and answer_tokens.issubset(segment["tokens"])
                    )
                )
            ):
                answer_hits.append(
                    {
                        "file_id": segment["file_id"],
                        "relative_path": segment["relative_path"],
                        "document_category": segment["document_category"],
                        "locator": segment["locator"],
                        "detected_subject_code": segment["detected_subject_code"],
                        "matched_answer_text": answer_text,
                        "passage": snippet(segment["text"], answer_tokens),
                    }
                )
        candidates.sort(key=lambda item: item["score"], reverse=True)
        answer_hits.sort(
            key=lambda item: (
                item["detected_subject_code"] != question["subject_code"],
                item["document_category"] not in {"course_outline", "lecture"},
                item["relative_path"],
                item["locator"],
            )
        )
        results.append(
            {
                "question_id": question["question_id"],
                "subject_code": question["subject_code"],
                "original_answer_status": question["answer_status"],
                "query_terms": sorted(query_tokens),
                "candidates": candidates[: args.limit],
                "answer_text_hits": answer_hits[: args.limit],
            }
        )

    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": (
            "Full local extraction of readable course-outline, lecture, summary, "
            "exercise, and other-academic-material files; IDF-weighted token overlap. "
            "Candidates are discovery aids, not verified evidence."
        ),
        "question_count": len(cohort),
        "source_file_count": len(
            {
                segment["file_id"]
                for segment in segments
            }
        ),
        "segment_count": segment_count,
        "extraction_errors": extraction_errors,
        "results": results,
    }
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Rechecked {len(cohort)} questions across "
        f"{payload['source_file_count']} local files / {segment_count} passages; "
        f"extraction errors={len(extraction_errors)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
