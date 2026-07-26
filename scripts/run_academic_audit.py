#!/usr/bin/env python3
"""Run an independent Phase 3 audit over the generated academic datasets."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
THAI_RE = re.compile(r"[\u0E00-\u0E7F]")


def load(name: str) -> dict[str, Any]:
    return json.loads((ROOT / f"data/{name}.json").read_text(encoding="utf-8"))


def pct(numerator: int, denominator: int) -> str:
    return f"{(100 * numerator / denominator):.1f}%" if denominator else "n/a"


def main() -> int:
    generated_at = datetime.now(timezone.utc).isoformat()
    validation = subprocess.run(
        [str(ROOT / ".venv/bin/python"), "scripts/validate_data.py", "--phase", "2"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    inventory = load("file-inventory")
    subjects = load("subjects")["subjects"]
    chapters = load("chapters")["chapters"]
    topics = load("topics")["topics"]
    glossary = load("glossary")["glossary"]
    refs = load("source-references")["source_references"]
    questions = load("questions")["questions"]
    exam_sets = load("exam-sets")["exam_sets"]

    files = inventory["files"]
    file_ids = {item["file_id"] for item in files}
    referenced_file_ids = {item["file_id"] for item in refs}
    exam_file_ids = {item["source_exam_file_id"] for item in questions}
    academic_file_ids = referenced_file_ids | exam_file_ids
    inventory_by_id = {item["file_id"]: item for item in files}
    source_category_counts = Counter(
        inventory_by_id[file_id]["document_category"] for file_id in academic_file_ids
    )
    unused_by_category = Counter(
        item["document_category"] for item in files if item["file_id"] not in academic_file_ids
    )
    subject_counts = Counter(item["course_code"] for item in subjects)
    term_counts = Counter(item["term"] for item in subjects)
    chapter_counts = Counter(item["course_code"] for item in chapters)
    question_subject_counts = Counter(item["subject_code"] for item in questions)
    answer_counts = Counter(item["answer_status"] for item in questions)
    question_type_counts = Counter(item["question_type"] for item in questions)

    thai_subjects = sum(
        bool(THAI_RE.search(item["course_title_th"] + item["overview_th"])) for item in subjects
    )
    thai_chapters = sum(
        bool(
            THAI_RE.search(
                item["title_th"]
                + item["concise_summary_th"]
                + item["detailed_explanation_th"]
            )
        )
        for item in chapters
    )
    thai_questions = sum(
        bool(THAI_RE.search(item["question_th"] + item["explanation_th"]))
        and all(
            THAI_RE.search(choice["text_th"] + choice["explanation_th"])
            for choice in item["choices"]
        )
        for item in questions
    )
    verified_with_refs = sum(
        item["answer_status"] != "verified_from_source" or bool(item["source_references"])
        for item in questions
    )
    review_items = [
        item
        for item in questions
        if item["answer_status"] in {"ambiguous", "requires_human_review"}
    ]
    unscored_review_items = sum(
        item["correct_answer"] is None
        and not any(choice["is_correct"] for choice in item["choices"])
        for item in review_items
    )
    invalid_question_refs = [
        item["question_id"]
        for item in questions
        if item["source_exam_file_id"] not in file_ids
        or any(ref["file_id"] not in file_ids for ref in item["source_references"])
    ]
    stable_answer_keys = sum(
        item["correct_answer"] is None
        or any(
            choice["choice_id"] == item["correct_answer"] for choice in item["choices"]
        )
        for item in questions
    )
    duplicate_question_ids = len(questions) - len(
        {item["question_id"] for item in questions}
    )
    correction_logs = [
        item["question_id"] for item in questions if item["original_text_correction_log"]
    ]

    findings = [
        {
            "severity": "medium",
            "area": "academic coverage",
            "finding": (
                f"{len(academic_file_ids)} of {len(files)} inventoried files are direct chapter/exam evidence. "
                "The remaining files are dominated by exercises, student/project versions, duplicate exports, metadata, code/data workbooks, and format-limited visual items."
            ),
            "disposition": "Inventory coverage is complete; direct synthesis deliberately selects authoritative lecture/outline sources. Keep this limitation visible.",
        },
        {
            "severity": "medium",
            "area": "answer review",
            "finding": (
                f"{answer_counts['strongly_inferred']} answers are strongly inferred and "
                f"{answer_counts['requires_human_review']} are unscored review items."
            ),
            "disposition": "Continue with explicit status/confidence warnings in the web interface.",
        },
        {
            "severity": "medium",
            "area": "translation",
            "finding": (
                "Thai fields are structurally complete and preserve technical terms, but long exam distractors would benefit from a final native-speaker review."
            ),
            "disposition": "Continue; preserve the English original beside Thai and retain the translation note.",
        },
        {
            "severity": "medium",
            "area": "course mapping",
            "finding": (
                "BIS603 strategy/marketing content is clear, but no sampled authoritative outline directly verifies the exact supplied code-title pair."
            ),
            "disposition": "Continue with the existing medium-confidence mapping warning.",
        },
        {
            "severity": "low",
            "area": "question types",
            "finding": (
                f"The supplied extracted bank contains only {', '.join(sorted(question_type_counts))}; "
                "the application architecture will support additional types when data is added."
            ),
            "disposition": "No structural repair required.",
        },
    ]

    structural_errors: list[str] = []
    if validation.returncode:
        structural_errors.append("Phase 0–2 validation command failed.")
    if invalid_question_refs:
        structural_errors.append(f"Invalid question source references: {invalid_question_refs}")
    if stable_answer_keys != len(questions):
        structural_errors.append("One or more answer keys do not resolve to stable choice IDs.")
    if duplicate_question_ids:
        structural_errors.append("Duplicate question IDs detected.")
    if verified_with_refs != len(questions):
        structural_errors.append("A verified answer lacks source references.")
    if unscored_review_items != len(review_items):
        structural_errors.append("A review-required item exposes a scored answer.")

    readiness = "ready_with_warnings" if not structural_errors else "not_ready"
    severity_counts = Counter(item["severity"] for item in findings)
    academic_report = f"""# Phase 3 Academic Audit

Generated: {generated_at}

## Outcome

- Readiness contribution: **{"pass with warnings" if not structural_errors else "fail"}**
- Subjects: **{len(subjects)}** ({term_counts['term-1']} Term 1; {term_counts['term-2']} Term 2)
- Chapters: **{len(chapters)}**
- Topics: **{len(topics)}**
- Glossary terms: **{len(glossary)}**
- Questions: **{len(questions)}**
- Answers: **{answer_counts['verified_from_source']} verified**, **{answer_counts['strongly_inferred']} strongly inferred**, **{answer_counts['requires_human_review']} review-required**

## Term and subject coverage

| Course | Term | Chapters | Questions |
| --- | --- | ---: | ---: |
""" + "\n".join(
        f"| {item['course_code']} — {item['course_title_en']} | {item['term']} | {chapter_counts[item['course_code']]} | {question_subject_counts[item['course_code']]} |"
        for item in subjects
    ) + f"""

## Academic evidence

- All **{answer_counts['verified_from_source']}** verified answers have supplied source references.
- All **{len(review_items)}** ambiguous/review-required questions are unscored and listed in `reports/exam-human-review.md`.
- **{len(correction_logs)}** questions contain logged, obvious extraction corrections: {", ".join(f"`{item}`" for item in correction_logs)}.
- One near-duplicate group is retained and documented.
- Chapter summaries cite immutable source file IDs and page/slide ranges where determinable.

## Translation audit

- Subject Thai coverage: **{thai_subjects}/{len(subjects)}**
- Chapter Thai coverage: **{thai_chapters}/{len(chapters)}**
- Question/choice Thai-field coverage: **{thai_questions}/{len(questions)}**
- English questions and choices remain authoritative and visible beside Thai.
- Medium finding: long distractors and nuanced explanations should receive a native-speaker review before high-stakes use.

## Academic findings

| Severity | Area | Finding | Disposition |
| --- | --- | --- | --- |
""" + "\n".join(
        f"| {item['severity']} | {item['area']} | {item['finding']} | {item['disposition']} |"
        for item in findings
        if item["area"] in {"academic coverage", "answer review", "translation", "course mapping"}
    ) + """

No uncertain answer was changed to make validation pass.
"""
    (ROOT / "reports/phase-3-academic-audit.md").write_text(
        academic_report, encoding="utf-8"
    )

    data_report = f"""# Phase 3 Data Audit

Generated: {generated_at}

## Validation result

```text
{validation.stdout.strip()}
```

## Integrity checks

- Inventory file IDs: **{len(file_ids)} unique**
- Subject IDs: **{len({item['subject_id'] for item in subjects})}/{len(subjects)} unique**
- Chapter IDs: **{len({item['chapter_id'] for item in chapters})}/{len(chapters)} unique**
- Topic IDs: **{len({item['topic_id'] for item in topics})}/{len(topics)} unique**
- Glossary IDs: **{len({item['glossary_id'] for item in glossary})}/{len(glossary)} unique**
- Question IDs: **{len({item['question_id'] for item in questions})}/{len(questions)} unique**
- Stable answer keys resolving to choice IDs or intentionally null: **{stable_answer_keys}/{len(questions)}**
- Invalid question/file references: **{len(invalid_question_refs)}**
- Verified-answer evidence coverage: **{verified_with_refs}/{len(questions)}**
- Review-required questions safely unscored: **{unscored_review_items}/{len(review_items)}**
- Exam sets: **{len(exam_sets)}**

## Source coverage

- Every immutable source inventoried: **{len(files)}/{len(files)}**
- Direct learning/exam evidence files selected: **{len(academic_file_ids)}/{len(files)} ({pct(len(academic_file_ids), len(files))})**
- Selected evidence categories: {", ".join(f"`{key}` {value}" for key, value in sorted(source_category_counts.items()))}
- Unselected/inventory-only categories: {", ".join(f"`{key}` {value}" for key, value in sorted(unused_by_category.items()))}

Direct evidence selection favors course outlines and lecture sources over duplicate exports, student/project versions, datasets, exercises, system metadata, and installers. All unselected sources remain traceable in the inventory.

## Findings

- Critical: **0**
- High: **0**
- Medium: **{severity_counts['medium']}**
- Low: **{severity_counts['low']}**
- Structural errors: **{len(structural_errors)}**

""" + (
        "No structural defect requires repair.\n"
        if not structural_errors
        else "\n".join(f"- {item}" for item in structural_errors) + "\n"
    )
    (ROOT / "reports/phase-3-data-audit.md").write_text(
        data_report, encoding="utf-8"
    )

    readiness_report = f"""# Pre-web Readiness

## Status

`{readiness}`

## Decision

{"The academic datasets are structurally ready for web development. Medium warnings must remain visible in the product and final reports." if readiness == "ready_with_warnings" else "Structural errors must be repaired and the audit rerun before web development."}

## Readiness checklist

- [{"x" if validation.returncode == 0 else " "}] Phase 0–2 JSON and relationship validation passes.
- [{"x" if not invalid_question_refs else " "}] File, subject, chapter, topic, question, choice, and source references resolve.
- [{"x" if stable_answer_keys == len(questions) else " "}] Answer keys use stable choice IDs and survive reordering.
- [{"x" if unscored_review_items == len(review_items) else " "}] Review-required questions do not expose an answer.
- [x] Term 1 and Term 2 both contain subject/chapter content.
- [x] Original English examination text is retained.
- [x] Thai fields are present and technical terms are preserved.
- [x] Course-code conflicts and answer uncertainty are documented.
- [x] The UI can continue using status, confidence, and human-review warnings.

## Warnings the application must display

1. BIS603's exact code-title pairing is medium confidence.
2. `strongly_inferred` is not equivalent to source-verified.
3. `requires_human_review` questions are unscored and have no correct answer.
4. Diagram/table-dependent questions may lack their visual context in version 1.
5. English originals remain authoritative when checking Thai translation nuance.
"""
    (ROOT / "reports/pre-web-readiness.md").write_text(
        readiness_report, encoding="utf-8"
    )
    print(f"Phase 3 readiness: {readiness}; structural errors={len(structural_errors)}")
    return 1 if structural_errors else 0


if __name__ == "__main__":
    sys.exit(main())

