#!/usr/bin/env python3
"""Independent source-boundary verification for the final visual release gate."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import fitz


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID = "file-7357a61279704b42"
SOURCE_PATH = ROOT / "แนวข้อสอบ.pdf"
TRIGGER = re.compile(
    r"following|shown below|diagram|figure|table|chart|image|code|"
    r"จากรูป|จากตาราง|ดังภาพ",
    re.IGNORECASE,
)
CODE_LIKE = re.compile(
    r"<[^>]+>|\bfunction\s+\w+\s*\(|background-color",
    re.IGNORECASE,
)


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def question_number(question: dict[str, Any]) -> int:
    return int(question["question_id"].rsplit("-", 1)[1])


def source_start(page: fitz.Page, number: int) -> float:
    candidates = [
        rect
        for rect in page.search_for(f"{number}.")
        if abs(rect.x0 - 72.0) <= 0.5
    ]
    if not candidates:
        raise RuntimeError(f"Question {number} start was not found")
    return min(rect.y0 for rect in candidates)


def main() -> int:
    checks = Checks()
    questions = load("data/questions.json")["questions"]
    source_map = load("data/question-source-map.json")["question_source_map"]
    inventory = load("data/file-inventory.json")["files"]
    document = fitz.open(SOURCE_PATH)
    by_id = {question["question_id"]: question for question in questions}
    map_by_id = {item["question_id"]: item for item in source_map}
    inventory_item = next(item for item in inventory if item["file_id"] == SOURCE_ID)
    source_digest = hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest()

    checks.require(len(questions) == len(by_id) == 105, "question bank must contain 105 unique questions")
    checks.require(len(source_map) == len(map_by_id) == 105, "source map must contain 105 unique questions")
    checks.require(set(by_id) == set(map_by_id), "question and source-map IDs differ")
    checks.require(source_digest == inventory_item["sha256"], "immutable source PDF hash differs from inventory")
    checks.require(len(document) == 16, "source exam must contain 16 pages")

    questions_by_page: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for question in questions:
        question_id = question["question_id"]
        mapping = map_by_id[question_id]
        checks.require(question["source_exam_file_id"] == SOURCE_ID, f"{question_id}: wrong source file")
        checks.require(mapping["exam_file_id"] == SOURCE_ID, f"{question_id}: source-map file differs")
        checks.require(
            question["source_page_or_slide"] == mapping["exam_page"],
            f"{question_id}: digital/source-map page differs",
        )
        questions_by_page[question["source_page_or_slide"]].append(question)

    boundaries: dict[str, tuple[float, float]] = {}
    content_bounds: dict[str, tuple[float, float, float, float]] = {}
    for page_number in range(1, 17):
        page = document[page_number - 1]
        page_questions = sorted(
            questions_by_page[page_number],
            key=question_number,
        )
        starts: list[float] = []
        for question in page_questions:
            try:
                starts.append(source_start(page, question_number(question)))
            except RuntimeError as exc:
                checks.errors.append(str(exc))
                starts.append(-1)
        checks.require(
            all(left < right for left, right in zip(starts, starts[1:])),
            f"page {page_number}: source question starts are not strictly ordered",
        )
        for index, question in enumerate(page_questions):
            question_id = question["question_id"]
            start = starts[index]
            end = starts[index + 1] if index + 1 < len(starts) else page.rect.height
            boundaries[question_id] = (start, end)
            words = [
                word
                for word in page.get_text("words")
                if word[1] >= start - 0.5 and word[1] < end - 0.1
            ]
            checks.require(bool(words), f"{question_id}: source boundary contains no text")
            if words:
                content_bounds[question_id] = (
                    min(word[0] for word in words),
                    min(word[1] for word in words),
                    max(word[2] for word in words),
                    max(word[3] for word in words),
                )

    discovered_visual_pairs: set[tuple[str, int]] = set()
    for page_number in range(1, 17):
        page = document[page_number - 1]
        page_questions = sorted(
            questions_by_page[page_number],
            key=lambda question: boundaries[question["question_id"]][0],
        )
        for xref in sorted({row[0] for row in page.get_images(full=True)}):
            rects = page.get_image_rects(xref)
            checks.require(bool(rects), f"page {page_number}: image xref {xref} has no placement")
            for rect in rects:
                center_y = (rect.y0 + rect.y1) / 2
                owners = [
                    question["question_id"]
                    for question in page_questions
                    if boundaries[question["question_id"]][0]
                    <= center_y
                    < boundaries[question["question_id"]][1]
                ]
                checks.require(
                    len(owners) == 1,
                    f"page {page_number}: image xref {xref} does not map to exactly one question",
                )
                if len(owners) == 1:
                    discovered_visual_pairs.add((owners[0], xref))

    recorded_visual_pairs: set[tuple[str, int]] = set()
    for question in questions:
        question_id = question["question_id"]
        page = document[question["source_page_or_slide"] - 1]
        start, end = boundaries[question_id]
        assets = question["visual_assets"]
        essential = [asset for asset in assets if asset["is_essential"]]
        references = [
            asset
            for asset in assets
            if asset["placement"] == "full_question_reference"
        ]
        checks.require(
            question["has_visual_content"] == bool(essential),
            f"{question_id}: has_visual_content conflicts with essential assets",
        )
        if essential:
            checks.require(len(essential) == 1, f"{question_id}: expected one essential source visual")
            checks.require(len(references) == 1, f"{question_id}: expected one full-question reference")
            asset = essential[0]
            xref = asset["source_object_xref"]
            recorded_visual_pairs.add((question_id, xref))
            actual_rects = page.get_image_rects(xref)
            checks.require(len(actual_rects) == 1, f"{question_id}: source object has ambiguous placement")
            if len(actual_rects) == 1:
                actual = actual_rects[0]
                recorded = asset["source_bbox"]
                checks.require(
                    all(
                        abs(value - expected) <= 0.02
                        for value, expected in (
                            (recorded["x"], actual.x0),
                            (recorded["y"], actual.y0),
                            (recorded["width"], actual.width),
                            (recorded["height"], actual.height),
                        )
                    ),
                    f"{question_id}: essential asset bbox differs from source object",
                )
            checks.require(
                asset["placement"] == "after_translation_before_choices",
                f"{question_id}: essential visual order differs from source",
            )

            reference = references[0]
            crop = reference["source_bbox"]
            crop_right = crop["x"] + crop["width"]
            crop_bottom = crop["y"] + crop["height"]
            content = content_bounds[question_id]
            checks.require(
                crop["y"] >= start - 0.25 and crop["y"] <= start + 0.05,
                f"{question_id}: reference crop starts outside its question boundary",
            )
            checks.require(
                crop_bottom >= content[3] - 0.05,
                f"{question_id}: reference crop cuts off source content",
            )
            checks.require(
                crop["x"] <= content[0] and crop_right >= content[2],
                f"{question_id}: reference crop cuts off horizontal source content",
            )
            if end < page.rect.height:
                checks.require(
                    crop_bottom <= end - 0.1,
                    f"{question_id}: reference crop includes the next question",
                )
            previous = [
                candidate
                for candidate in questions_by_page[question["source_page_or_slide"]]
                if boundaries[candidate["question_id"]][1] == start
            ]
            if previous:
                previous_bottom = content_bounds[previous[0]["question_id"]][3]
                checks.require(
                    crop["y"] >= previous_bottom + 0.05,
                    f"{question_id}: reference crop includes the previous question",
                )
        else:
            checks.require(not references, f"{question_id}: text-only item has a reference crop")

    checks.require(
        discovered_visual_pairs == recorded_visual_pairs,
        "embedded source visuals and recorded question assets do not map one-to-one: "
        f"source={sorted(discovered_visual_pairs)}, recorded={sorted(recorded_visual_pairs)}",
    )

    trigger_ids: list[str] = []
    code_ids: list[str] = []
    for question in questions:
        searchable = " ".join(
            [
                question["original_question_en"],
                question["question_th"],
                *[
                    text
                    for choice in question["choices"]
                    for text in (choice["original_text_en"], choice["text_th"])
                ],
            ]
        )
        if TRIGGER.search(searchable):
            trigger_ids.append(question["question_id"])
        if CODE_LIKE.search(searchable):
            code_ids.append(question["question_id"])

    checks.require(
        {"question-comprehensive-098", "question-comprehensive-099"}.issubset(code_ids),
        "HTML/JavaScript formatting-priority questions were not detected",
    )
    visual_ids = sorted(question_id for question_id, _ in discovered_visual_pairs)
    print(
        "Final source-boundary verification: "
        f"{'PASS' if not checks.errors else 'FAIL'} "
        f"({len(checks.errors)} errors)"
    )
    print(f"Questions checked: {len(questions)} across {len(document)} pages")
    print(f"Keyword-priority questions checked: {len(trigger_ids)}")
    print(f"Code-format priority questions checked: {len(code_ids)}")
    print(f"Embedded source visuals mapped: {len(discovered_visual_pairs)}")
    print("Essential visual question IDs: " + ", ".join(visual_ids))
    for error in checks.errors:
        print(f"ERROR: {error}")
    return 1 if checks.errors else 0


if __name__ == "__main__":
    sys.exit(main())
