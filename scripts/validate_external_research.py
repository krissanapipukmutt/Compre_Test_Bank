#!/usr/bin/env python3
"""Validate Phase 7 provenance, probability, preservation, and scoring rules."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tarfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
WARNING_EN = (
    "This answer is a probability-based recommendation. It is not verified by "
    "the supplied course materials or by a sufficiently authoritative external source."
)
WARNING_TH = (
    "คำตอบนี้เป็นข้อเสนอแนะจากการวิเคราะห์ความน่าจะเป็นและการตัดตัวเลือก "
    "ไม่ได้รับการยืนยันจากเอกสารการเรียนหรือแหล่งข้อมูลภายนอกที่น่าเชื่อถือเพียงพอ"
)
STATUSES = {
    "verified_from_course_material",
    "verified_from_external_source",
    "strongly_supported_by_external_source",
    "probabilistic_recommendation",
    "unresolvable_question",
}
ORIGINS = {
    "COURSE_MATERIAL",
    "EXTERNAL_AUTHORITATIVE",
    "PROBABILISTIC_REASONING_ONLY",
}
RESEARCH_FIELDS = {
    "original_answer_status", "final_answer_status", "evidence_origin",
    "answer_source_type", "external_source_ids", "external_evidence_summary_en",
    "external_evidence_summary_th", "final_answer", "final_explanation_en",
    "final_explanation_th", "confidence", "confidence_percentage",
    "confidence_rationale_en", "confidence_rationale_th",
    "probability_distribution", "elimination_reasoning_en",
    "elimination_reasoning_th", "unresolved_reason", "requires_human_review",
    "research_completed_at", "research_audit_log",
}
PLACEHOLDER = re.compile(r"\b(?:todo|tbd|placeholder|example\.com|insert (?:source|url))\b", re.I)


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)

    def warn(self, condition: bool, message: str) -> None:
        if not condition:
            self.warnings.append(message)


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def original_questions() -> list[dict[str, Any]]:
    backups = sorted((ROOT / "backups").glob("pre-external-research-*.tar.gz"))
    if not backups:
        raise FileNotFoundError("No pre-external-research backup exists")
    with tarfile.open(backups[-1], "r:gz") as archive:
        member = archive.extractfile("data/questions.json")
        if member is None:
            raise FileNotFoundError("Backup has no data/questions.json")
        return json.loads(member.read().decode("utf-8"))["questions"]


def validate(check_links: bool) -> Checks:
    checks = Checks()
    questions = load("data/questions.json")["questions"]
    sources = load("data/external-sources.json")["external_sources"]
    evidence = load("data/external-answer-evidence.json")["external_answer_evidence"]
    recommendations = load("data/probabilistic-recommendations.json")
    reviews = load("data/question-review-status.json")["question_review_status"]
    originals = original_questions()

    question_by_id = {item["question_id"]: item for item in questions}
    source_by_id = {item["source_id"]: item for item in sources}
    evidence_by_id = {item["question_id"]: item for item in evidence}
    review_by_id = {item["question_id"]: item for item in reviews}
    original_by_id = {item["question_id"]: item for item in originals}

    checks.require(len(question_by_id) == len(questions) == 105, "questions must contain 105 unique IDs")
    checks.require(len(source_by_id) == len(sources), "external source IDs must be unique")
    checks.require(len(evidence_by_id) == len(evidence) == 89, "external evidence must cover 89 unique researched questions")
    checks.require(len(review_by_id) == len(reviews) == 105, "review status must cover all 105 questions")
    checks.require(set(question_by_id) == set(original_by_id), "question IDs changed relative to backup")
    checks.require(set(question_by_id) == set(review_by_id), "review status IDs do not match questions")
    counts = Counter(item["answer_status"] for item in questions)
    expected_counts = {
        "verified_from_course_material": 49,
        "verified_from_external_source": 47,
        "strongly_supported_by_external_source": 2,
        "probabilistic_recommendation": 2,
        "unresolvable_question": 5,
    }
    checks.require(dict(counts) == expected_counts, f"unexpected final status counts: {dict(counts)}")

    normalized_urls: set[str] = set()
    for item in sources:
        sid = item.get("source_id", "<missing>")
        for field in ("organization_or_author", "title", "url", "accessed_date"):
            checks.require(bool(item.get(field)), f"{sid}: missing {field}")
        parsed = urlparse(str(item.get("url", "")))
        checks.require(parsed.scheme == "https" and bool(parsed.netloc), f"{sid}: invalid external URL")
        normalized = str(item.get("url", "")).rstrip("/").lower()
        checks.require(normalized not in normalized_urls, f"{sid}: duplicate external URL")
        normalized_urls.add(normalized)
        checks.require(not PLACEHOLDER.search(json.dumps(item, ensure_ascii=False)), f"{sid}: placeholder text detected")
        checks.require(bool(item.get("applicable_question_ids")), f"{sid}: no applicable questions")
        for question_id in item.get("applicable_question_ids", []):
            checks.require(question_id in question_by_id, f"{sid}: unknown applicable question {question_id}")

    for question_id, item in question_by_id.items():
        original = original_by_id[question_id]
        status = item.get("answer_status")
        checks.require(status in STATUSES, f"{question_id}: invalid final status {status}")
        checks.require(item.get("final_answer_status") == status, f"{question_id}: final status mismatch")
        checks.require(item.get("evidence_origin") in ORIGINS, f"{question_id}: invalid evidence origin")
        checks.require(item.get("final_answer") == item.get("correct_answer"), f"{question_id}: final answer mismatch")
        checks.require(item.get("original_answer") == original.get("correct_answer"), f"{question_id}: original answer not preserved")
        checks.require(item.get("original_answer_status") == original.get("answer_status"), f"{question_id}: original status not preserved")
        checks.require(item.get("original_explanation_en") == original.get("explanation_en"), f"{question_id}: original English explanation not preserved")
        checks.require(item.get("original_explanation_th") == original.get("explanation_th"), f"{question_id}: original Thai explanation not preserved")
        checks.require(item.get("original_course_material_references") == original.get("source_references"), f"{question_id}: original course references not preserved")
        checks.require(item.get("original_choices") == original.get("choices"), f"{question_id}: original choice records not preserved")
        checks.require(item.get("original_question_en") == original.get("original_question_en"), f"{question_id}: English question changed")
        checks.require(item.get("question_th") == original.get("question_th"), f"{question_id}: Thai question changed")
        current_choice_text = [(x["choice_id"], x["original_text_en"], x["text_th"]) for x in item["choices"]]
        original_choice_text = [(x["choice_id"], x["original_text_en"], x["text_th"]) for x in original["choices"]]
        checks.require(current_choice_text == original_choice_text, f"{question_id}: question choice text changed")
        answer = item.get("correct_answer")
        marked = [choice["choice_id"] for choice in item["choices"] if choice.get("is_correct")]
        checks.require(marked == ([] if answer is None else [answer]), f"{question_id}: answer key/choice flag mismatch")
        review = review_by_id[question_id]
        checks.require(review.get("answer_status") == status, f"{question_id}: review status mismatch")
        checks.require(review.get("evidence_origin") == item.get("evidence_origin"), f"{question_id}: review origin mismatch")
        checks.require(review.get("requires_human_review") == item.get("requires_human_review"), f"{question_id}: review flag mismatch")

        if question_id in evidence_by_id:
            checks.require(RESEARCH_FIELDS.issubset(item), f"{question_id}: missing researched fields")
            checks.require(bool(item.get("research_completed_at")), f"{question_id}: missing completion time")
            checks.require(len(item.get("research_audit_log", [])) >= 3, f"{question_id}: incomplete audit log")

        source_ids = item.get("external_source_ids", [])
        checks.require(all(source_id in source_by_id for source_id in source_ids), f"{question_id}: unknown external source ID")
        if status in {"verified_from_external_source", "strongly_supported_by_external_source"}:
            checks.require(item.get("evidence_origin") == "EXTERNAL_AUTHORITATIVE", f"{question_id}: external answer mislabeled")
            checks.require(bool(source_ids), f"{question_id}: externally supported without a source")
            checks.require(all(question_id in source_by_id[source_id]["applicable_question_ids"] for source_id in source_ids), f"{question_id}: source applicability mismatch")
        if status == "verified_from_course_material":
            checks.require(item.get("evidence_origin") == "COURSE_MATERIAL", f"{question_id}: course answer origin mismatch")
            checks.require(not source_ids, f"{question_id}: course answer incorrectly references external source")
        if status == "probabilistic_recommendation":
            distribution = item.get("probability_distribution", [])
            checks.require(item.get("evidence_origin") == "PROBABILISTIC_REASONING_ONLY", f"{question_id}: probability origin mismatch")
            checks.require(not source_ids, f"{question_id}: probability answer claims an external source")
            checks.require(sum(row.get("probability_percentage", -1000) for row in distribution) == 100, f"{question_id}: probabilities do not total 100")
            checks.require(len(distribution) == len(item["choices"]), f"{question_id}: incomplete probability distribution")
            checks.require(item.get("probability_warning_en") == WARNING_EN, f"{question_id}: English warning differs")
            checks.require(item.get("probability_warning_th") == WARNING_TH, f"{question_id}: Thai warning differs")
            checks.require(item.get("requires_human_review") is True, f"{question_id}: probability answer must require review")
            top = max(row["probability_percentage"] for row in distribution)
            checks.require(50 <= top < 100, f"{question_id}: invalid top probability")
            checks.require(review.get("scoring_eligibility") == "practice_judgment_unscored", f"{question_id}: unsafe scoring eligibility")
        if status == "unresolvable_question":
            checks.require(answer is None and not marked, f"{question_id}: unresolvable answer is exposed")
            checks.require(item.get("requires_human_review") is True, f"{question_id}: unresolved must require review")
            checks.require(review.get("scoring_eligibility") == "excluded", f"{question_id}: unresolved included in scoring")
        if status == "strongly_supported_by_external_source":
            checks.require(review.get("scoring_eligibility") == "opt_in_external", f"{question_id}: strong external is not opt-in")

    recs = recommendations.get("probabilistic_recommendations", [])
    checks.require(recommendations.get("required_warning_en") == WARNING_EN, "probability file English warning differs")
    checks.require(recommendations.get("required_warning_th") == WARNING_TH, "probability file Thai warning differs")
    checks.require(len(recs) == 2, "probability file must contain exactly two recommendations")
    for item in recs:
        checks.require(sum(row["probability_percentage"] for row in item["probability_distribution"]) == 100, f"{item.get('question_id')}: recommendation probabilities do not total 100")
        checks.require(item.get("warning_en") == WARNING_EN and item.get("warning_th") == WARNING_TH, f"{item.get('question_id')}: recommendation warning differs")
        checks.require(item.get("human_review_required") is True, f"{item.get('question_id')}: recommendation lacks review flag")

    if check_links:
        def check_source(item: dict[str, Any]) -> tuple[str, int | None, str | None]:
            result = subprocess.run(
                [
                    "curl", "--location", "--silent", "--show-error",
                    "--output", "/dev/null", "--write-out", "%{http_code}",
                    "--connect-timeout", "10", "--max-time", "20",
                    "--user-agent", "Mozilla/5.0 Phase7SourceValidator/1.0",
                    item["url"],
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            try:
                status = int(result.stdout[-3:])
            except (ValueError, IndexError):
                status = None
            error = result.stderr.strip() if result.returncode != 0 else None
            return item["source_id"], status, error

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(check_source, sources))
        for source_id, status, error in results:
            if error is not None:
                checks.errors.append(f"{source_id}: URL check failed: {error}")
            elif status is not None and status < 400:
                continue
            elif status in {401, 403}:
                # These codes prove a live endpoint but restrict automated clients.
                checks.warnings.append(
                    f"{source_id}: endpoint resolved but automated access returned HTTP {status}"
                )
            else:
                checks.errors.append(f"{source_id}: HTTP {status}")
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-links", action="store_true")
    args = parser.parse_args()
    checks = validate(args.check_links)
    for warning in checks.warnings:
        print(f"WARNING: {warning}")
    for error in checks.errors:
        print(f"ERROR: {error}")
    print(
        "Phase 7 external-research validation: "
        f"{'PASS' if not checks.errors else 'FAIL'} "
        f"({len(checks.errors)} errors, {len(checks.warnings)} warnings)"
    )
    return 1 if checks.errors else 0


if __name__ == "__main__":
    sys.exit(main())
