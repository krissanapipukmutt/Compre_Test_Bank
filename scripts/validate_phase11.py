#!/usr/bin/env python3
"""Validate Phase 11 learning enrichment and question-structure preservation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
WEB_DATA = ROOT / "web/src/data"
EXPECTED_CANDIDATES = {
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
ALLOWED_CATEGORIES = {
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


class Audit:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def check_pair(audit: Audit, english: Any, thai: Any, label: str) -> None:
    audit.require(nonempty(english), f"{label} English is blank")
    audit.require(nonempty(thai), f"{label} Thai is blank")
    if nonempty(english) and nonempty(thai):
        audit.require(english.strip() != thai.strip(), f"{label} repeats English in Thai")
        audit.require(
            any("\u0e00" <= char <= "\u0e7f" for char in thai),
            f"{label} Thai contains no Thai",
        )


def check_label(audit: Audit, item: dict[str, Any], label: str) -> None:
    category = item.get("source_category")
    audit.require(category in ALLOWED_CATEGORIES, f"{label} has invalid source category")
    if category not in ALLOWED_CATEGORIES:
        return
    expected_en, expected_th = ALLOWED_CATEGORIES[category]
    audit.require(item.get("source_label_en") == expected_en, f"{label} English label mismatch")
    audit.require(item.get("source_label_th") == expected_th, f"{label} Thai label mismatch")


def check_source_integrity(audit: Audit) -> None:
    inventory = read_json(DATA / "file-inventory.json")
    checked = 0
    for item in inventory["files"]:
        if (
            item.get("readable_status") == "ignored_metadata"
            or item.get("document_category") == "system_metadata"
        ):
            continue
        path = ROOT / item["relative_path"]
        audit.require(path.is_file(), f"academic source missing: {item['relative_path']}")
        if not path.is_file():
            continue
        checked += 1
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        audit.require(digest == item["sha256"], f"academic source changed: {item['relative_path']}")
        audit.require(path.stat().st_size == item["size_bytes"], f"academic source size changed: {item['relative_path']}")
    audit.require(checked > 300, "unexpectedly few immutable academic sources checked")


def check_synced(audit: Audit, names: tuple[str, ...]) -> None:
    for name in names:
        audit.require(
            (DATA / name).read_bytes() == (WEB_DATA / name).read_bytes(),
            f"{name} root/web copies differ",
        )


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


def check_library(audit: Audit) -> tuple[int, int, int, int]:
    subjects = read_json(DATA / "subjects.json")["subjects"]
    chapters = read_json(DATA / "chapters.json")["chapters"]
    topics = read_json(DATA / "topics.json")["topics"]
    glossary = read_json(DATA / "glossary.json")["glossary"]
    references = read_json(DATA / "source-references.json")["source_references"]
    reference_ids = {item["source_reference_id"] for item in references}
    glossary_ids = {item["glossary_id"] for item in glossary}
    audit.require(len(subjects) == 6, "subject count must remain 6")
    audit.require(len(chapters) == 44, "chapter count must remain 44")
    audit.require(len(topics) == 132, "topic count must remain 132")
    supplemental_sections = 0

    for subject in subjects:
        label = subject["subject_id"]
        audit.require(subject.get("content_status") == "enriched", f"{label} not enriched")
        audit.require(len(subject.get("learning_objectives_en", [])) >= 3, f"{label} objectives missing")
        audit.require(
            len(subject.get("learning_objectives_en", []))
            == len(subject.get("learning_objectives_th", [])),
            f"{label} objective counts differ",
        )
        check_pair(audit, subject.get("overview_en"), subject.get("overview_th"), f"{label} overview")
        audit.require(len(subject.get("lesson_sections", [])) >= 2, f"{label} lesson sections missing")
        for section in subject.get("lesson_sections", []):
            check_label(audit, section, f"{label}.{section.get('section_id')}")
            audit.require(
                set(section.get("source_reference_ids", [])).issubset(reference_ids),
                f"{label} section has invalid source reference",
            )

    for chapter in chapters:
        label = chapter["chapter_id"]
        audit.require(chapter.get("content_status") == "enriched", f"{label} not enriched")
        audit.require(len(chapter.get("learning_objectives_en", [])) >= 3, f"{label} objectives missing")
        audit.require(
            len(chapter.get("learning_objectives_en", []))
            == len(chapter.get("learning_objectives_th", [])),
            f"{label} objective counts differ",
        )
        check_pair(audit, chapter.get("overview_en"), chapter.get("overview_th"), f"{label} overview")
        audit.require(len(chapter.get("lesson_sections", [])) >= 2, f"{label} lesson sections missing")
        for section in chapter.get("lesson_sections", []):
            check_label(audit, section, f"{label}.{section.get('section_id')}")
            if section.get("source_category") == "supplementary_explanation":
                supplemental_sections += 1
        for formula in chapter.get("formula_details", []):
            check_label(audit, formula, f"{label} formula {formula.get('formula')}")
            audit.require(len(formula.get("variables", [])) >= 1, f"{label} formula variables missing")
            check_pair(audit, formula.get("meaning_en"), formula.get("meaning_th"), f"{label} formula meaning")
            check_pair(audit, formula.get("when_en"), formula.get("when_th"), f"{label} formula use")
            check_pair(audit, formula.get("example_en"), formula.get("example_th"), f"{label} formula example")
            check_pair(audit, formula.get("mistake_en"), formula.get("mistake_th"), f"{label} formula mistake")

    for topic in topics:
        label = topic["topic_id"]
        audit.require(topic.get("content_status") == "enriched", f"{label} not enriched")
        audit.require(len(topic.get("learning_objectives_en", [])) >= 3, f"{label} objectives missing")
        audit.require(
            len(topic.get("learning_objectives_en", []))
            == len(topic.get("learning_objectives_th", [])),
            f"{label} objective counts differ",
        )
        check_pair(audit, topic.get("overview_en"), topic.get("overview_th"), f"{label} overview")
        audit.require(len(topic.get("lesson_sections", [])) >= 3, f"{label} lesson sections missing")
        audit.require(len(topic.get("key_terms", [])) >= 1, f"{label} key terms missing")
        audit.require(len(topic.get("comparisons", [])) >= 1, f"{label} comparison missing")
        audit.require(len(topic.get("process_steps", [])) >= 3, f"{label} workflow missing")
        audit.require(len(topic.get("examples", [])) >= 1, f"{label} example missing")
        audit.require(len(topic.get("common_misunderstandings", [])) >= 1, f"{label} misunderstandings missing")
        audit.require(len(topic.get("quick_review", {}).get("key_points_en", [])) >= 3, f"{label} quick review missing")
        related = set(topic.get("quick_review", {}).get("related_glossary_ids", []))
        audit.require(bool(related) and related.issubset(glossary_ids), f"{label} glossary links invalid")
        audit.require(
            set(topic.get("source_reference_ids", [])).issubset(reference_ids),
            f"{label} source reference invalid",
        )
        for section in topic.get("lesson_sections", []):
            check_label(audit, section, f"{label}.{section.get('section_id')}")
            if section.get("source_category") == "course_material":
                audit.require(
                    bool(section.get("source_reference_ids")),
                    f"{label} course section has no source",
                )
            if section.get("source_category") == "supplementary_explanation":
                supplemental_sections += 1
        for collection in ("key_terms", "comparisons", "process_steps", "examples", "common_misunderstandings"):
            for index, item in enumerate(topic.get(collection, [])):
                check_label(audit, item, f"{label}.{collection}[{index}]")
        for comparison in topic.get("comparisons", []):
            audit.require(len(comparison.get("rows", [])) >= 1, f"{label} comparison rows missing")
            audit.require(
                set(comparison.get("source_reference_ids", [])).issubset(reference_ids),
                f"{label} comparison source invalid",
            )
        for formula in topic.get("formulas", []):
            check_label(audit, formula, f"{label} formula {formula.get('formula')}")
            audit.require(len(formula.get("variables", [])) >= 1, f"{label} formula variables missing")
            check_pair(audit, formula.get("meaning_en"), formula.get("meaning_th"), f"{label} formula meaning")
            check_pair(audit, formula.get("example_en"), formula.get("example_th"), f"{label} formula example")
        focus = topic.get("exam_focus", {})
        check_label(audit, focus, f"{label}.exam_focus")
        audit.require(len(focus.get("points_en", [])) >= 2, f"{label} exam focus missing")
        audit.require(
            len(focus.get("points_en", [])) == len(focus.get("points_th", [])),
            f"{label} exam focus bilingual count differs",
        )
    return len(subjects), len(chapters), len(topics), supplemental_sections


def check_questions(audit: Audit) -> tuple[int, int, int, int]:
    questions = read_json(DATA / "questions.json")["questions"]
    baseline = read_json(DATA / "question-structure-preservation-baseline.json")
    expected = {row["question_id"]: row for row in baseline["questions"]}
    detected: set[str] = set()
    display_only = 0
    human_review = 0
    audit.require(len(questions) == 105, "question count must remain 105")
    audit.require(len(expected) == 105, "question preservation baseline must contain 105")
    for question in questions:
        question_id = question["question_id"]
        audit.require(answer_snapshot(question) == expected.get(question_id), f"{question_id} answer-bearing data changed")
        audit.require(
            question.get("raw_original_question_en") == question["original_question_en"],
            f"{question_id} raw English not preserved",
        )
        audit.require(
            question.get("raw_original_question_th") == question["question_th"],
            f"{question_id} raw Thai not preserved",
        )
        status = question.get("normalization_status")
        audit.require(
            status in {"not_required", "normalized", "display_formatted_only", "ambiguous", "requires_human_review"},
            f"{question_id} normalization status invalid",
        )
        if question.get("embedded_choices_detected"):
            detected.add(question_id)
            options = question.get("embedded_options", [])
            audit.require(status == "normalized", f"{question_id} detected but not normalized")
            audit.require(len(options) >= 2, f"{question_id} embedded options missing")
            audit.require(
                question.get("normalized_question_en") != question["original_question_en"],
                f"{question_id} normalized English unchanged",
            )
            audit.require(
                question.get("normalized_question_th") != question["question_th"],
                f"{question_id} normalized Thai unchanged",
            )
            audit.require(
                len({option.get("marker") for option in options}) == len(options),
                f"{question_id} duplicate embedded markers",
            )
            for option in options:
                check_pair(
                    audit,
                    option.get("original_text_en"),
                    option.get("text_th"),
                    f"{question_id}.{option.get('embedded_option_id')}",
                )
            audit.require(
                len(question.get("normalization_audit_log", [])) >= 1,
                f"{question_id} normalization audit missing",
            )
        else:
            audit.require(status == "not_required", f"{question_id} false-positive status")
            audit.require(not question.get("embedded_options"), f"{question_id} unexpected embedded options")
            audit.require(
                question.get("normalized_question_en") == question["original_question_en"],
                f"{question_id} unnecessary English normalization",
            )
        if status == "display_formatted_only":
            display_only += 1
        if status in {"ambiguous", "requires_human_review"} or question.get(
            "normalization_requires_human_review"
        ):
            human_review += 1
    audit.require(detected == EXPECTED_CANDIDATES, f"candidate set mismatch: {sorted(detected)}")
    return len(questions), len(detected), display_only, human_review


def main() -> int:
    audit = Audit()
    check_source_integrity(audit)
    check_synced(audit, ("subjects.json", "chapters.json", "topics.json", "questions.json"))
    subjects, chapters, topics, supplemental = check_library(audit)
    questions, normalized, display_only, human_review = check_questions(audit)
    if audit.errors:
        for error in audit.errors:
            print(f"ERROR: {error}")
        print(f"Phase 11 validation: FAIL ({len(audit.errors)} errors)")
        return 1
    print(
        "Phase 11 validation: PASS "
        f"({subjects} subjects, {chapters} chapters, {topics} topics, "
        f"{supplemental} supplementary lesson sections; {questions} questions, "
        f"{normalized} normalized, {display_only} display-only, "
        f"{human_review} structure-review)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
