#!/usr/bin/env python3
"""Validate bilingual completeness and preservation of academic source data."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_PATH = ROOT / "data" / "questions.json"
WEB_QUESTIONS_PATH = ROOT / "web" / "src" / "data" / "questions.json"
BASELINE_PATH = ROOT / "data" / "translation-preservation-baseline.json"
GLOSSARY_PATH = ROOT / "data" / "translation-glossary.json"

PLACEHOLDERS = (
    "คำศัพท์/ข้อความภาษาอังกฤษตามต้นฉบับ",
    "translation pending",
    "untranslated",
    "todo",
    "n/a",
)
ALLOWED_STATUSES = {"verified", "repaired", "incomplete", "ambiguous", "requires_human_review"}
ALLOWED_QUALITIES = {"high", "medium", "low"}
READY_STATUSES = {"verified", "repaired"}
THAI_RE = re.compile(r"[\u0E00-\u0E7F]")
LATIN_WORD_RE = re.compile(r"[A-Za-z]{2,}")
CODE_RE = re.compile(
    r"^(?:<[^>]+>.*|(?:create|new|function|def)\s+\w+\(\)|"
    r"(?:IPv[\d.]+|RIP|BGP|OSPF|TCP|IP|PHP|React|Node\.js|AngularJS|Flutter|"
    r"React Native|Kotlin|Ionic|Git|Postman|Docker|Figma|Sketch|WPA|UML))$"
)
NUMERIC_RE = re.compile(r"^[\d\s.,−+\-/:;=()]+$")


def number_from_id(question_id: str) -> int:
    return int(question_id.rsplit("-", 1)[1])


def is_approved_literal(value: str, review_note: str = "") -> bool:
    stripped = value.strip()
    identifier_core = stripped.replace("และ", " ").replace("and", " ").replace(",", " ")
    identifier_tokens = identifier_core.split()
    identifier_list = bool(identifier_tokens) and all(
        re.fullmatch(r"(?:[A-Z][A-Za-z0-9_]*|[0-9]+)", token) for token in identifier_tokens
    )
    return bool(
        NUMERIC_RE.fullmatch(stripped)
        or NUMERIC_RE.fullmatch(stripped.replace("และ", " "))
        or CODE_RE.fullmatch(stripped)
        or identifier_list
        or ("คง" in review_note and ("โค้ด" in review_note or "ชื่อเฉพาะ" in review_note or "ตัวระบุ" in review_note))
    )


def english_density(value: str) -> float:
    latin = sum(len(word) for word in LATIN_WORD_RE.findall(value))
    thai = len(THAI_RE.findall(value))
    return latin / max(1, latin + thai)


def validate_pair(
    *,
    label: str,
    english: Any,
    thai: Any,
    errors: list[str],
    warnings: list[str],
    review_note: str = "",
    forbid_answer_marker: bool = False,
) -> None:
    if not isinstance(english, str) or not english.strip():
        errors.append(f"{label}: missing English source")
        return
    if not isinstance(thai, str) or not thai.strip():
        errors.append(f"{label}: missing Thai translation")
        return
    lowered = thai.casefold()
    if any(placeholder in lowered for placeholder in PLACEHOLDERS):
        errors.append(f"{label}: contains placeholder text")
    if thai.strip() == english.strip() and not is_approved_literal(thai, review_note):
        errors.append(f"{label}: Thai is identical to English without a reviewed literal/proper-name exemption")
    if forbid_answer_marker and ("คำตอบ:" in thai or "correct answer" in lowered):
        errors.append(f"{label}: translation contains an answer marker")
    if (
        len(english) >= 24
        and len(THAI_RE.findall(thai)) < 4
        and not is_approved_literal(thai, review_note)
    ):
        errors.append(f"{label}: long source has no meaningful Thai content")
    if (
        len(english) >= 50
        and english_density(thai) > 0.72
        and not is_approved_literal(thai, review_note)
    ):
        errors.append(f"{label}: translation contains excessive English text ({english_density(thai):.0%})")
    if len(english) >= 80 and len(thai) / len(english) < 0.28:
        warnings.append(f"{label}: translation is unusually short and requires contextual confirmation")


def fingerprint(question: dict[str, Any]) -> dict[str, Any]:
    return {
        "question_id": question["question_id"],
        "original_question_en": question["original_question_en"],
        "choice_order": [choice["choice_id"] for choice in question["choices"]],
        "choice_english": [choice["original_text_en"] for choice in question["choices"]],
        "choice_correctness": [choice["is_correct"] for choice in question["choices"]],
        "correct_answer": question.get("correct_answer"),
        "final_answer": question.get("final_answer"),
        "original_answer": question.get("original_answer"),
        "acceptable_answers": question.get("acceptable_answers"),
        "answer_status": question.get("answer_status"),
        "final_answer_status": question.get("final_answer_status"),
    }


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    payload = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    web_payload = json.loads(WEB_QUESTIONS_PATH.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    glossary = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))

    if payload != web_payload:
        errors.append("web/src/data/questions.json is not synchronized with data/questions.json")
    if payload.get("schema_version") != "9.0":
        errors.append("questions schema_version must be 9.0")
    questions = payload.get("questions")
    if not isinstance(questions, list) or len(questions) != 105:
        errors.append(f"expected 105 questions, found {len(questions) if isinstance(questions, list) else 'invalid'}")
        questions = questions if isinstance(questions, list) else []

    baseline_by_id = {entry["question_id"]: entry for entry in baseline["questions"]}
    ids: set[str] = set()
    choice_ids: set[str] = set()
    for question in questions:
        qid = question.get("question_id", "<missing>")
        if qid in ids:
            errors.append(f"{qid}: duplicate question ID")
        ids.add(qid)
        if qid not in baseline_by_id:
            errors.append(f"{qid}: absent from preservation baseline")
        elif fingerprint(question) != baseline_by_id[qid]:
            errors.append(f"{qid}: English source, ID/order, correctness, or academic answer changed")

        status = question.get("translation_status")
        quality = question.get("translation_quality")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{qid}: invalid translation_status {status!r}")
        if quality not in ALLOWED_QUALITIES:
            errors.append(f"{qid}: invalid translation_quality {quality!r}")
        for field in ("translation_review_note", "translation_completed_at"):
            if not isinstance(question.get(field), str) or not question[field].strip():
                errors.append(f"{qid}: missing {field}")
        if not isinstance(question.get("translation_audit_log"), list) or not question["translation_audit_log"]:
            errors.append(f"{qid}: missing translation_audit_log")

        validate_pair(
            label=f"{qid}.question",
            english=question.get("original_question_en"),
            thai=question.get("question_th"),
            errors=errors,
            warnings=warnings,
            forbid_answer_marker=True,
        )
        en = question.get("original_question_en", "").casefold()
        th = question.get("question_th", "")
        required_markers = [
            (("such as", "for example"), ("เช่น", "ตัวอย่าง")),
            (("following table", "following diagram", "shown below"), ("ต่อไปนี้", "ด้านล่าง")),
            ((" not ", "not ", "incorrect", "except"), ("ไม่", "ยกเว้น")),
            ((" only",), ("เท่านั้น", "เฉพาะ", "เพียง")),
        ]
        for english_markers, thai_markers in required_markers:
            if any(marker in en for marker in english_markers) and not any(marker in th for marker in thai_markers):
                warnings.append(
                    f"{qid}.question: source condition {english_markers[0]!r} needs contextual confirmation"
                )

        choices = question.get("choices", [])
        if len(choices) != 5:
            errors.append(f"{qid}: expected five choices, found {len(choices)}")
        for choice in choices:
            cid = choice.get("choice_id", "<missing>")
            if cid in choice_ids:
                errors.append(f"{cid}: duplicate choice ID")
            choice_ids.add(cid)
            validate_pair(
                label=f"{cid}.choice",
                english=choice.get("original_text_en"),
                thai=choice.get("text_th"),
                errors=errors,
                warnings=warnings,
                review_note=choice.get("translation_review_note", ""),
                forbid_answer_marker=True,
            )
            validate_pair(
                label=f"{cid}.explanation",
                english=choice.get("explanation_en"),
                thai=choice.get("explanation_th"),
                errors=errors,
                warnings=warnings,
            )
            if choice.get("translation_status") not in {"verified", "repaired"}:
                errors.append(f"{cid}: invalid or non-ready choice translation status")
            if not choice.get("translation_review_note"):
                errors.append(f"{cid}: missing choice translation review note")

        for index, original_choice in enumerate(question.get("original_choices", [])):
            validate_pair(
                label=f"{qid}.original_choices[{index}]",
                english=original_choice.get("original_text_en"),
                thai=original_choice.get("text_th"),
                errors=errors,
                warnings=warnings,
                review_note=next(
                    (
                        choice.get("translation_review_note", "")
                        for choice in choices
                        if choice["choice_id"] == original_choice.get("choice_id")
                    ),
                    "",
                ),
            )

        for english_field, thai_field in (
            ("explanation_en", "explanation_th"),
            ("original_explanation_en", "original_explanation_th"),
            ("final_explanation_en", "final_explanation_th"),
            ("translation_note", "translation_note_th"),
        ):
            validate_pair(
                label=f"{qid}.{thai_field}",
                english=question.get(english_field),
                thai=question.get(thai_field),
                errors=errors,
                warnings=warnings,
            )
        if question.get("external_evidence_summary_en"):
            validate_pair(
                label=f"{qid}.external_evidence_summary",
                english=question["external_evidence_summary_en"],
                thai=question.get("external_evidence_summary_th"),
                errors=errors,
                warnings=warnings,
            )
        if question.get("probability_warning_en"):
            validate_pair(
                label=f"{qid}.probability_warning",
                english=question["probability_warning_en"],
                thai=question.get("probability_warning_th"),
                errors=errors,
                warnings=warnings,
            )
        if question.get("remaining_uncertainty") and not question.get("remaining_uncertainty_th"):
            errors.append(f"{qid}: missing remaining_uncertainty_th")
        if question.get("unresolved_reason") and not question.get("unresolved_reason_th"):
            errors.append(f"{qid}: missing unresolved_reason_th")

    if ids != set(baseline_by_id):
        errors.append("question ID set differs from the preservation baseline")

    terms = glossary.get("terms", [])
    if len(terms) < 15:
        errors.append("translation glossary must contain at least 15 reviewed terms")
    normalized_terms = [term.get("term_en", "").casefold() for term in terms]
    if len(normalized_terms) != len(set(normalized_terms)):
        errors.append("translation glossary contains duplicate English terms")
    for index, term in enumerate(terms):
        for field in (
            "term_en",
            "preferred_term_th",
            "alternative_terms_th",
            "subject_codes",
            "notes",
            "source_reference",
        ):
            if field not in term:
                errors.append(f"glossary term {index}: missing {field}")

    ready_count = sum(question.get("translation_status") in READY_STATUSES for question in questions)
    result = {
        "questions": len(questions),
        "choices": sum(len(question.get("choices", [])) for question in questions),
        "ready_translations": ready_count,
        "human_review_translations": len(questions) - ready_count,
        "glossary_terms": len(terms),
        "warnings": len(warnings),
        "errors": len(errors),
    }
    print(json.dumps(result, ensure_ascii=False))
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
