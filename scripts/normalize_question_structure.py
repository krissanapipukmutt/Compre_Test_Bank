#!/usr/bin/env python3
"""Normalize source-verified embedded statement blocks without changing answers."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import fitz


ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_PATH = ROOT / "data/questions.json"
WEB_QUESTIONS_PATH = ROOT / "web/src/data/questions.json"
BASELINE_PATH = ROOT / "data/question-structure-preservation-baseline.json"
SOURCE_PATH = ROOT / "แนวข้อสอบ.pdf"
COMPLETED_AT = "2026-07-28T09:00:00+07:00"

CANDIDATE_IDS = {
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
GENERIC_MARKER_PATTERNS = (
    ("parenthesized_letter", re.compile(r"(?:^|\s)\(([A-Ea-e])\)\s+"), "letter"),
    ("letter_parenthesis", re.compile(r"(?:^|\s)([A-Ea-e])\)\s*"), "letter"),
    ("letter_period", re.compile(r"(?:^|\s)([A-Ea-e])\.\s+"), "letter"),
    ("number_parenthesis", re.compile(r"(?:^|\s)([1-5])\)\s+"), "number"),
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_space(value: str) -> str:
    return " ".join(value.split()).strip()


def comparable(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", normalized_space(value).casefold())


def detect_embedded_marker_pattern(text: str) -> str | None:
    """Conservatively flag sequential embedded markers; never rewrite here."""
    candidates: list[tuple[int, str]] = []
    for name, pattern, kind in GENERIC_MARKER_PATTERNS:
        matches = list(pattern.finditer(text))
        if len(matches) < 2:
            continue
        markers = [match.group(1).upper() for match in matches]
        values = (
            [ord(marker) - ord("A") for marker in markers]
            if kind == "letter"
            else [int(marker) - 1 for marker in markers]
        )
        if any(
            marker_value != values[index - 1] + 1
            for index, marker_value in enumerate(values)
            if index
        ):
            continue
        if not text[: matches[0].start()].strip():
            continue
        candidates.append((len(matches), name))
    return max(candidates, default=(0, ""))[1] or None


def audit_candidate_ids(questions: list[dict[str, Any]]) -> set[str]:
    detected = {
        question["question_id"]
        for question in questions
        if detect_embedded_marker_pattern(question["original_question_en"])
    }
    if detected != CANDIDATE_IDS:
        missing = sorted(CANDIDATE_IDS - detected)
        unexpected = sorted(detected - CANDIDATE_IDS)
        raise ValueError(
            "embedded-marker candidate scan changed: "
            f"missing={missing}, unexpected={unexpected}"
        )
    return detected


def split_letter_statements(value: str) -> tuple[str, list[tuple[str, str]]]:
    matches = list(re.finditer(r"(?<!\w)([A-C])\)\s*", value))
    if len(matches) != 3 or [match.group(1) for match in matches] != ["A", "B", "C"]:
        raise ValueError("expected one ordered A)/B)/C) statement block")
    stem = value[: matches[0].start()].strip()
    options: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(value)
        options.append((match.group(1), value[match.end() : end].strip()))
    return stem, options


def answer_snapshot(question: dict[str, Any]) -> dict[str, Any]:
    return {
        "question_id": question["question_id"],
        "original_question_en": question["original_question_en"],
        "question_th": question["question_th"],
        "choices": copy.deepcopy(question["choices"]),
        "original_choices": copy.deepcopy(question["original_choices"]),
        "correct_answer": copy.deepcopy(question["correct_answer"]),
        "acceptable_answers": copy.deepcopy(question["acceptable_answers"]),
        "original_answer": copy.deepcopy(question["original_answer"]),
        "final_answer": copy.deepcopy(question["final_answer"]),
    }


def write_baseline(questions: list[dict[str, Any]]) -> None:
    if BASELINE_PATH.exists():
        return
    payload = {
        "schema_version": "1.0.0",
        "created_at": COMPLETED_AT,
        "purpose": (
            "Preserve raw bilingual question text, selectable choices, and every "
            "answer pointer before Phase 11 display-structure normalization."
        ),
        "questions": [answer_snapshot(question) for question in questions],
    }
    BASELINE_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def source_page_text(document: fitz.Document, page_number: int) -> str:
    return normalized_space(document[page_number - 1].get_text("text"))


def verify_against_source(
    question: dict[str, Any],
    english_options: list[tuple[str, str]],
    page_text: str,
) -> None:
    if question["source_exam_relative_path"] != "แนวข้อสอบ.pdf":
        raise ValueError(f"{question['question_id']} is not mapped to the source PDF")
    comparable_page = comparable(page_text)
    for _, option_text in english_options:
        probe = comparable(option_text)[:48]
        if len(probe) < 12 or probe not in comparable_page:
            raise ValueError(
                f"{question['question_id']} statement not found on source page: "
                f"{option_text[:70]}"
            )


def normalize_question(
    question: dict[str, Any],
    document: fitz.Document,
) -> dict[str, Any]:
    original = answer_snapshot(question)
    question_id = question["question_id"]
    raw_en = question["original_question_en"]
    raw_th = question["question_th"]
    question["raw_original_question_en"] = raw_en
    question["raw_original_question_th"] = raw_th
    question["normalized_question_en"] = raw_en
    question["normalized_question_th"] = raw_th
    question["embedded_choices_detected"] = False
    question["embedded_choice_pattern"] = None
    question["embedded_options"] = []
    question["normalization_status"] = "not_required"
    question["normalization_confidence"] = "high"
    question["normalization_audit_log"] = []
    question["normalization_requires_human_review"] = False
    question["normalization_human_review_note"] = None

    if question_id not in CANDIDATE_IDS:
        return question

    stem_en, statements_en = split_letter_statements(raw_en)
    stem_th, statements_th = split_letter_statements(raw_th)
    verify_against_source(
        question,
        statements_en,
        source_page_text(document, question["source_page_or_slide"]),
    )
    if len(statements_en) != len(statements_th):
        raise ValueError(f"{question_id} English/Thai statement counts differ")

    source_markers = ["1", "2", "3"] if question_id == "question-comprehensive-028" else [
        "A",
        "B",
        "C",
    ]
    embedded_options: list[dict[str, Any]] = []
    for index, ((_, english), (_, thai)) in enumerate(
        zip(statements_en, statements_th, strict=True)
    ):
        marker = source_markers[index]
        embedded_options.append(
            {
                "embedded_option_id": f"{question_id}-statement-{index + 1}",
                "marker": marker,
                "original_text_en": english,
                "text_th": thai,
                "source_page_or_slide": question["source_page_or_slide"],
            }
        )

    raw_digest = hashlib.sha256(raw_en.encode("utf-8")).hexdigest()
    question["normalized_question_en"] = stem_en
    question["normalized_question_th"] = stem_th
    question["embedded_choices_detected"] = True
    question["embedded_choice_pattern"] = (
        "source_numbered_statements_1_2_3"
        if question_id == "question-comprehensive-028"
        else "letter_parenthesis_A_B_C"
    )
    question["embedded_options"] = embedded_options
    question["normalization_status"] = "normalized"
    question["normalization_audit_log"] = [
        {
            "completed_at": COMPLETED_AT,
            "action": "source_verified_embedded_statement_normalization",
            "source_file_id": question["source_exam_file_id"],
            "source_relative_path": question["source_exam_relative_path"],
            "source_page_or_slide": question["source_page_or_slide"],
            "raw_question_sha256": raw_digest,
            "detected_pattern": question["embedded_choice_pattern"],
            "result": (
                "Separated the learner-facing bilingual stem and embedded "
                "statement lines; preserved raw text, selectable choices, choice "
                "IDs, ordering, and all answer pointers."
            ),
            "answer_key_before": copy.deepcopy(original["correct_answer"]),
            "answer_key_after": copy.deepcopy(question["correct_answer"]),
            "choice_ids_preserved": True,
            "human_review_required": False,
        }
    ]

    if answer_snapshot(question) != original:
        raise ValueError(f"{question_id} answer-bearing fields changed")
    return question


def validate_existing_baseline(questions: list[dict[str, Any]]) -> None:
    baseline = read_json(BASELINE_PATH)
    expected = {
        row["question_id"]: row for row in baseline.get("questions", [])
    }
    if len(expected) != len(questions):
        raise ValueError("question preservation baseline cardinality mismatch")
    for question in questions:
        if answer_snapshot(question) != expected.get(question["question_id"]):
            raise ValueError(
                f"{question['question_id']} no longer matches the Phase 11 baseline"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate existing normalized records without rewriting JSON.",
    )
    args = parser.parse_args()

    payload = read_json(QUESTIONS_PATH)
    questions = payload["questions"]
    detected_ids = audit_candidate_ids(questions)
    write_baseline(questions)
    validate_existing_baseline(questions)

    document = fitz.open(SOURCE_PATH)
    normalized = [
        normalize_question(copy.deepcopy(question), document)
        for question in questions
    ]
    normalized_by_id = {question["question_id"]: question for question in normalized}

    if args.check:
        for existing in questions:
            expected = normalized_by_id[existing["question_id"]]
            for field in (
                "raw_original_question_en",
                "raw_original_question_th",
                "normalized_question_en",
                "normalized_question_th",
                "embedded_choices_detected",
                "embedded_choice_pattern",
                "embedded_options",
                "normalization_status",
                "normalization_confidence",
                "normalization_requires_human_review",
                "normalization_human_review_note",
            ):
                if existing.get(field) != expected.get(field):
                    raise ValueError(
                        f"{existing['question_id']} has invalid {field}"
                    )
        print(
            "Question structure validation: PASS "
            f"({len(questions)} audited, {len(detected_ids)} normalized, "
            "0 display-only, 0 structure-review)"
        )
        return 0

    # Phase 11 is an additive question-display schema extension. Retain the
    # established Phase 9 question schema version used by preservation gates.
    payload["schema_version"] = "9.0"
    payload["questions"] = normalized
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    QUESTIONS_PATH.write_text(rendered, encoding="utf-8")
    WEB_QUESTIONS_PATH.write_text(rendered, encoding="utf-8")
    print(
        f"Normalized {len(detected_ids)} source-verified questions; "
        f"audited {len(questions)} total questions."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
