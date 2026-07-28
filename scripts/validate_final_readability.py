#!/usr/bin/env python3
"""Validate final Study Library completeness and question readability data."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EXPECTED_EMBEDDED_IDS = {
    "question-comprehensive-004",
    "question-comprehensive-006",
    "question-comprehensive-007",
    "question-comprehensive-008",
    "question-comprehensive-009",
    "question-comprehensive-010",
    "question-comprehensive-019",
    "question-comprehensive-020",
    "question-comprehensive-028",
}
SOURCE_LABELS = {
    "course_material": (
        "From course materials",
        "จากเอกสารการเรียน",
    ),
    "supplementary_explanation": (
        "Supplementary explanation",
        "คำอธิบายเสริม",
    ),
    "external_authoritative_source": (
        "Supplementary information from an authoritative external source",
        "ข้อมูลเสริมจากแหล่งภายนอกที่น่าเชื่อถือ",
    ),
}
MARKER_PATTERNS = (
    (re.compile(r"(?:^|\s)\(([A-Ea-e])\)\s+"), "letter"),
    (re.compile(r"(?:^|\s)([A-Ea-e])\)\s*"), "letter"),
    (re.compile(r"(?:^|\s)([A-Ea-e])\.\s+"), "letter"),
    (re.compile(r"(?:^|\s)([1-5])\)\s+"), "number"),
)


class Audit:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(name: str) -> dict[str, Any]:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def answer_snapshot(question: dict[str, Any]) -> dict[str, Any]:
    return {
        "question_id": question["question_id"],
        "original_question_en": question["original_question_en"],
        "question_th": question["question_th"],
        "choices": question["choices"],
        "original_choices": question["original_choices"],
        "correct_answer": question["correct_answer"],
        "acceptable_answers": question["acceptable_answers"],
        "original_answer": question["original_answer"],
        "final_answer": question["final_answer"],
    }


def sequential_marker_count(value: str) -> int:
    best = 0
    for pattern, kind in MARKER_PATTERNS:
        matches = list(pattern.finditer(value))
        if len(matches) < 2:
            continue
        markers = [match.group(1).upper() for match in matches]
        marker_values = (
            [ord(marker) - ord("A") for marker in markers]
            if kind == "letter"
            else [int(marker) - 1 for marker in markers]
        )
        if all(
            current == marker_values[index - 1] + 1
            for index, current in enumerate(marker_values)
            if index
        ):
            best = max(best, len(matches))
    return best


def bilingual_character_counts(topic: dict[str, Any]) -> tuple[int, int]:
    english = 0
    thai = 0

    def visit(value: Any, language: str | None = None) -> None:
        nonlocal english, thai
        if isinstance(value, str):
            if language == "en":
                english += len(value)
            elif language == "th":
                thai += len(value)
            return
        if isinstance(value, list):
            for item in value:
                visit(item, language)
            return
        if isinstance(value, dict):
            for key, item in value.items():
                next_language = (
                    "en"
                    if key.endswith("_en") or key in {"formula", "memory_aid"}
                    else "th"
                    if key.endswith("_th")
                    else language
                )
                visit(item, next_language)

    for field in (
        "learning_objectives_en",
        "learning_objectives_th",
        "overview_en",
        "overview_th",
        "lesson_sections",
        "key_terms",
        "comparisons",
        "process_steps",
        "formulas",
        "examples",
        "common_misunderstandings",
        "exam_focus",
        "quick_review",
    ):
        visit(topic.get(field))
    return english, thai


def validate_source_label(
    audit: Audit,
    item: dict[str, Any],
    label: str,
) -> None:
    category = item.get("source_category")
    audit.require(category in SOURCE_LABELS, f"{label} has invalid source category")
    if category not in SOURCE_LABELS:
        return
    expected_en, expected_th = SOURCE_LABELS[category]
    audit.require(item.get("source_label_en") == expected_en, f"{label} English source label mismatch")
    audit.require(item.get("source_label_th") == expected_th, f"{label} Thai source label mismatch")


def validate_topics(audit: Audit) -> tuple[int, int, int, Counter[str]]:
    topics = read_json("topics.json")["topics"]
    references = read_json("source-references.json")["source_references"]
    reference_ids = {reference["source_reference_id"] for reference in references}
    audit.require(len(topics) == 132, "topic count must remain 132")
    minimum_english = 10**9
    minimum_thai = 10**9
    categories: Counter[str] = Counter()

    for topic in topics:
        topic_id = topic["topic_id"]
        audit.require(topic.get("content_status") == "enriched", f"{topic_id} is not enriched")
        audit.require(len(topic.get("learning_objectives_en", [])) >= 3, f"{topic_id} has too few English objectives")
        audit.require(
            len(topic.get("learning_objectives_en", []))
            == len(topic.get("learning_objectives_th", [])),
            f"{topic_id} bilingual objective counts differ",
        )
        audit.require(bool(topic.get("overview_en")), f"{topic_id} English overview is blank")
        audit.require(bool(topic.get("overview_th")), f"{topic_id} Thai overview is blank")
        audit.require(len(topic.get("lesson_sections", [])) >= 3, f"{topic_id} is summary-only")
        audit.require(len(topic.get("key_terms", [])) >= 1, f"{topic_id} key terms missing")
        audit.require(len(topic.get("comparisons", [])) >= 1, f"{topic_id} comparison missing")
        audit.require(len(topic.get("process_steps", [])) >= 3, f"{topic_id} workflow missing")
        audit.require(len(topic.get("examples", [])) >= 1, f"{topic_id} example missing")
        audit.require(
            len(topic.get("common_misunderstandings", [])) >= 1,
            f"{topic_id} misunderstanding guidance missing",
        )
        audit.require(
            len(topic.get("quick_review", {}).get("key_points_en", [])) >= 3,
            f"{topic_id} quick review missing",
        )
        audit.require(
            bool(topic.get("source_reference_ids"))
            and set(topic["source_reference_ids"]).issubset(reference_ids),
            f"{topic_id} has missing or invalid source references",
        )

        course_sections = 0
        supplementary_sections = 0
        for section in topic.get("lesson_sections", []):
            section_label = f"{topic_id}.{section.get('section_id')}"
            validate_source_label(audit, section, section_label)
            categories[section.get("source_category", "invalid")] += 1
            english = section.get("content_en", [])
            thai = section.get("content_th", [])
            audit.require(bool(english), f"{section_label} English content is blank")
            audit.require(bool(thai), f"{section_label} Thai content is blank")
            audit.require(
                len(english) == len(thai),
                f"{section_label} bilingual paragraph counts differ",
            )
            if section.get("source_category") == "course_material":
                course_sections += 1
                audit.require(
                    bool(section.get("source_reference_ids"))
                    and set(section["source_reference_ids"]).issubset(reference_ids),
                    f"{section_label} course source reference is missing or invalid",
                )
            elif section.get("source_category") == "supplementary_explanation":
                supplementary_sections += 1
        audit.require(course_sections >= 2, f"{topic_id} needs at least two course-material sections")
        audit.require(
            supplementary_sections >= 1,
            f"{topic_id} supplementary reasoning section is missing",
        )

        for collection in (
            "key_terms",
            "comparisons",
            "process_steps",
            "formulas",
            "examples",
            "common_misunderstandings",
        ):
            for index, item in enumerate(topic.get(collection, [])):
                validate_source_label(audit, item, f"{topic_id}.{collection}[{index}]")
        validate_source_label(audit, topic["exam_focus"], f"{topic_id}.exam_focus")

        english_chars, thai_chars = bilingual_character_counts(topic)
        minimum_english = min(minimum_english, english_chars)
        minimum_thai = min(minimum_thai, thai_chars)
        audit.require(
            english_chars >= 1_500,
            f"{topic_id} has insufficient structured English content ({english_chars} characters)",
        )
        audit.require(
            thai_chars >= 1_200,
            f"{topic_id} has insufficient structured Thai content ({thai_chars} characters)",
        )
    return len(topics), minimum_english, minimum_thai, categories


def validate_questions(audit: Audit) -> tuple[int, int, int]:
    questions = read_json("questions.json")["questions"]
    baseline = read_json("question-structure-preservation-baseline.json")
    baseline_by_id = {
        question["question_id"]: question for question in baseline["questions"]
    }
    audit.require(len(questions) == 105, "question count must remain 105")
    audit.require(len(baseline_by_id) == 105, "preservation baseline must contain 105 questions")
    marker_ids: set[str] = set()
    duplicate_count = 0

    for question in questions:
        question_id = question["question_id"]
        audit.require(
            answer_snapshot(question) == baseline_by_id.get(question_id),
            f"{question_id} raw or answer-bearing data changed",
        )
        audit.require(
            question.get("raw_original_question_en")
            == question["original_question_en"],
            f"{question_id} raw English is not preserved",
        )
        audit.require(
            question.get("raw_original_question_th") == question["question_th"],
            f"{question_id} raw Thai is not preserved",
        )
        audit.require(bool(question.get("normalized_question_en")), f"{question_id} normalized English is blank")
        audit.require(bool(question.get("normalized_question_th")), f"{question_id} normalized Thai is blank")

        marker_count = sequential_marker_count(question["original_question_en"])
        if marker_count:
            marker_ids.add(question_id)
            options = question.get("embedded_options", [])
            audit.require(question.get("embedded_choices_detected") is True, f"{question_id} marker sequence was not detected")
            audit.require(question.get("normalization_status") == "normalized", f"{question_id} is not safely normalized")
            audit.require(len(options) == marker_count, f"{question_id} structured statement count differs from raw markers")
            audit.require(
                not question.get("normalization_requires_human_review"),
                f"{question_id} remains in format review",
            )
            for option in options:
                audit.require(bool(option.get("original_text_en")), f"{question_id} embedded English is blank")
                audit.require(bool(option.get("text_th")), f"{question_id} embedded Thai is blank")

        stem = normalized(question["normalized_question_en"])
        structured_choices = {
            normalized(choice["original_text_en"])
            for choice in question["choices"]
            if len(normalized(choice["original_text_en"]).split()) >= 2
        }
        embedded_statements = {
            normalized(option["original_text_en"])
            for option in question.get("embedded_options", [])
        }
        duplicated = embedded_statements & structured_choices
        if duplicated:
            duplicate_count += 1
            audit.errors.append(
                f"{question_id} duplicates embedded statements as structured choices"
            )
        for choice in structured_choices:
            if choice in stem:
                duplicate_count += 1
                audit.errors.append(
                    f"{question_id} normalized stem contains a full structured choice"
                )

    audit.require(
        marker_ids == EXPECTED_EMBEDDED_IDS,
        f"embedded marker set changed: {sorted(marker_ids)}",
    )
    return len(questions), len(marker_ids), duplicate_count


def main() -> int:
    audit = Audit()
    topic_count, min_english, min_thai, categories = validate_topics(audit)
    question_count, marker_count, duplicate_count = validate_questions(audit)
    if audit.errors:
        for error in audit.errors:
            print(f"ERROR: {error}")
        print(f"Final readability validation: FAIL ({len(audit.errors)} errors)")
        return 1
    print(
        "Final readability validation: PASS "
        f"({topic_count} complete topics; minimum structured content "
        f"{min_english} English/{min_thai} Thai characters; "
        f"topic lesson labels {dict(categories)}; {question_count} questions, "
        f"{marker_count} marker-bearing, {duplicate_count} duplicated)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
