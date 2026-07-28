#!/usr/bin/env python3
"""Validate complete, bidirectional, source-safe exam-to-study coverage."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = "e722f98"

FORBIDDEN_MAPPING_KEYS = {
    "correct_answer",
    "final_answer",
    "recommended_answer",
    "answer_choice",
    "probability_distribution",
    "elimination_reasoning",
    "explanation_en",
    "explanation_th",
    "is_correct",
}
ANSWER_PRESERVATION_FIELDS = (
    "correct_answer",
    "original_answer",
    "final_answer",
    "answer_status",
    "original_answer_status",
    "final_answer_status",
    "explanation_en",
    "explanation_th",
    "original_explanation_en",
    "original_explanation_th",
    "final_explanation_en",
    "final_explanation_th",
    "evidence_origin",
    "answer_source_type",
    "external_source_ids",
    "confidence",
    "confidence_percentage",
    "requires_human_review",
    "probability_distribution",
    "elimination_reasoning_en",
    "elimination_reasoning_th",
    "remaining_uncertainty",
    "remaining_uncertainty_th",
    "unresolved_reason",
    "unresolved_reason_th",
)


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def keys_recursive(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from keys_recursive(item)
    elif isinstance(value, list):
        for item in value:
            yield from keys_recursive(item)


def baseline_questions() -> list[dict]:
    result = subprocess.run(
        ["git", "show", f"{BASELINE_COMMIT}:data/questions.json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)["questions"]


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []

    questions_payload = load("data/questions.json")
    topics_payload = load("data/topics.json")
    coverage_payload = load("data/question-study-coverage.json")
    map_payload = load("data/study-topic-question-map.json")
    references = load("data/source-references.json")["source_references"]
    external_sources = load("data/external-sources.json")["external_sources"]

    if questions_payload != load("web/src/data/questions.json"):
        errors.append("root/web question data are not synchronized")
    if topics_payload != load("web/src/data/topics.json"):
        errors.append("root/web topic data are not synchronized")
    if coverage_payload != load("web/src/data/question-study-coverage.json"):
        errors.append("root/web question coverage data are not synchronized")
    if map_payload != load("web/src/data/study-topic-question-map.json"):
        errors.append("root/web topic-question map data are not synchronized")

    questions = questions_payload["questions"]
    topics = topics_payload["topics"]
    coverage = coverage_payload["question_study_coverage"]
    topic_map = map_payload["study_topic_question_map"]
    question_by_id = {item["question_id"]: item for item in questions}
    topic_by_id = {item["topic_id"]: item for item in topics}
    coverage_by_id = {item["question_id"]: item for item in coverage}
    map_by_id = {item["topic_id"]: item for item in topic_map}
    reference_ids = {item["source_reference_id"] for item in references}
    external_ids = {item["source_id"] for item in external_sources}

    for label, values, identifier in (
        ("questions", questions, "question_id"),
        ("topics", topics, "topic_id"),
        ("question coverage", coverage, "question_id"),
        ("topic map", topic_map, "topic_id"),
    ):
        ids = [item[identifier] for item in values]
        if len(ids) != len(set(ids)):
            errors.append(f"{label} contain duplicate {identifier} values")

    if len(questions) != 105:
        errors.append(f"expected 105 questions, found {len(questions)}")
    if len(topics) != 132:
        errors.append(f"expected 132 topics, found {len(topics)}")
    if set(question_by_id) != set(coverage_by_id):
        errors.append("question coverage does not contain exactly all question IDs")
    if set(topic_by_id) != set(map_by_id):
        errors.append("topic map does not contain exactly all topic IDs")

    forbidden = FORBIDDEN_MAPPING_KEYS.intersection(keys_recursive(coverage_payload))
    if forbidden:
        errors.append(
            "coverage mapping contains answer-leakage keys: "
            + ", ".join(sorted(forbidden))
        )
    serialized_coverage = json.dumps(coverage_payload, ensure_ascii=False)
    if "choice-" in serialized_coverage:
        errors.append("coverage mapping contains a choice identifier")

    final_statuses = Counter()
    origins = Counter()
    warning_ids = []
    for question_id, record in coverage_by_id.items():
        question = question_by_id.get(question_id)
        if not question:
            continue
        related = record.get("related_study_topic_ids", [])
        primary = record.get("primary_study_topic_id")
        if not related or primary not in related:
            errors.append(f"{question_id}: invalid related/primary topic link")
        if record.get("current_coverage_status") != "fully_covered":
            errors.append(f"{question_id}: concept remains uncovered")
        final_statuses[record.get("final_coverage_status")] += 1
        origin = record.get("evidence_origin")
        origins[origin] += 1
        if origin not in {
            "COURSE_MATERIAL",
            "EXTERNAL_AUTHORITATIVE",
            "SUPPLEMENTARY_EXPLANATION",
        }:
            errors.append(f"{question_id}: invalid evidence origin {origin}")
        source_refs = set(record.get("source_reference_ids", []))
        ext_refs = set(record.get("external_source_ids", []))
        if not source_refs.issubset(reference_ids):
            errors.append(f"{question_id}: invalid course source reference")
        if not ext_refs.issubset(external_ids):
            errors.append(f"{question_id}: invalid external source reference")
        if origin == "EXTERNAL_AUTHORITATIVE" and not ext_refs:
            errors.append(f"{question_id}: external coverage has no external source")
        if not record.get("tested_concept_en") or not record.get("tested_concept_th"):
            errors.append(f"{question_id}: tested concept is not bilingual")
        if not record.get("tested_skill"):
            errors.append(f"{question_id}: tested skill is missing")
        if record.get("answer_status_warning"):
            warning_ids.append(question_id)
        expected_warning = (
            question["requires_human_review"]
            or question["answer_status"]
            in {
                "probabilistic_recommendation",
                "unresolvable_question",
                "strongly_supported_by_external_source",
            }
        )
        if bool(record.get("answer_status_warning")) != expected_warning:
            errors.append(f"{question_id}: answer-status warning is inconsistent")

        teaching_sections = [
            section
            for section in topic_by_id[primary]["lesson_sections"]
            if question_id in section.get("related_question_ids", [])
        ]
        if not teaching_sections:
            errors.append(f"{question_id}: no linked teaching section in {primary}")
        if not any(
            section.get("evidence_origin") == origin
            for section in teaching_sections
        ):
            errors.append(f"{question_id}: teaching-section origin mismatch")

    reverse_links = 0
    for topic_id, record in map_by_id.items():
        related = record.get("related_question_ids", [])
        reverse_links += len(related)
        if record.get("question_count") != len(related):
            errors.append(f"{topic_id}: declared question count is inconsistent")
        if len(record.get("tested_concepts", [])) != len(related):
            errors.append(f"{topic_id}: concept count differs from question count")
        difficulty = record.get("difficulty_counts", {})
        if sum(difficulty.get(level, 0) for level in ("easy", "medium", "hard")) != len(related):
            errors.append(f"{topic_id}: difficulty counts are inconsistent")
        warning_count = sum(
            bool(coverage_by_id[question_id]["answer_status_warning"])
            for question_id in related
            if question_id in coverage_by_id
        )
        if record.get("answer_status_warning_count") != warning_count:
            errors.append(f"{topic_id}: warning count is inconsistent")
        expected_signal = (
            "no_supplied_exam_example_found"
            if not related
            else "appears_in_supplied_exam_examples"
            if len(related) == 1
            else "appears_multiple_times_in_supplied_exam_examples"
        )
        if record.get("exam_frequency_signal") != expected_signal:
            errors.append(f"{topic_id}: exam frequency signal is inconsistent")
        for question_id in related:
            if question_id not in question_by_id:
                errors.append(f"{topic_id}: unknown related question {question_id}")
            elif topic_id not in coverage_by_id[question_id]["related_study_topic_ids"]:
                errors.append(f"{topic_id}: one-way link to {question_id}")
    if reverse_links != len(questions):
        errors.append(
            f"expected 105 precise reverse links, found {reverse_links}"
        )

    coverage_section_count = 0
    for topic in topics:
        for section in topic["lesson_sections"]:
            if not section["section_id"].startswith("coverage-"):
                continue
            coverage_section_count += 1
            if section.get("evidence_origin") not in {
                "COURSE_MATERIAL",
                "EXTERNAL_AUTHORITATIVE",
                "SUPPLEMENTARY_EXPLANATION",
            }:
                errors.append(
                    f"{section['section_id']}: missing or invalid evidence origin"
                )
            if len(section.get("content_en", [])) != len(section.get("content_th", [])):
                errors.append(f"{section['section_id']}: bilingual content mismatch")
            if not section.get("related_question_ids"):
                errors.append(f"{section['section_id']}: no related questions")
            content = " ".join(
                section.get("content_en", []) + section.get("content_th", [])
            )
            if "question-comprehensive-" in content or "choice-" in content:
                errors.append(f"{section['section_id']}: answer-oriented ID leaked into lesson")
            if not set(section.get("source_reference_ids", [])).issubset(reference_ids):
                errors.append(f"{section['section_id']}: invalid source reference")
            if not set(section.get("external_source_ids", [])).issubset(external_ids):
                errors.append(f"{section['section_id']}: invalid external reference")

    try:
        baseline = {item["question_id"]: item for item in baseline_questions()}
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        errors.append(f"could not load answer-preservation baseline: {exc}")
        baseline = {}
    for question_id, question in question_by_id.items():
        prior = baseline.get(question_id)
        if not prior:
            errors.append(f"{question_id}: missing from answer-preservation baseline")
            continue
        changed = [
            field
            for field in ANSWER_PRESERVATION_FIELDS
            if question.get(field) != prior.get(field)
        ]
        current_choices = [
            {
                "choice_id": choice["choice_id"],
                "is_correct": choice["is_correct"],
                "explanation_en": choice["explanation_en"],
                "explanation_th": choice["explanation_th"],
            }
            for choice in question["choices"]
        ]
        prior_choices = [
            {
                "choice_id": choice["choice_id"],
                "is_correct": choice["is_correct"],
                "explanation_en": choice["explanation_en"],
                "explanation_th": choice["explanation_th"],
            }
            for choice in prior["choices"]
        ]
        if current_choices != prior_choices:
            changed.append("choice answer/explanation fields")
        if changed:
            errors.append(
                f"{question_id}: academic answer data changed: {', '.join(changed)}"
            )

    print("Exam-to-Study-Library coverage validation")
    print(f"- Questions: {len(questions)}")
    print(f"- Study topics: {len(topics)}")
    print(f"- Precise bidirectional links: {reverse_links}")
    print(f"- Added/confirmed coverage lessons: {coverage_section_count}")
    print(
        "- Initial coverage: "
        + ", ".join(
            f"{key}={value}"
            for key, value in sorted(
                Counter(item["initial_coverage_status"] for item in coverage).items()
            )
        )
    )
    print(
        "- Final coverage: "
        + ", ".join(f"{key}={value}" for key, value in sorted(final_statuses.items()))
    )
    print(
        "- Evidence origins: "
        + ", ".join(f"{key}={value}" for key, value in sorted(origins.items()))
    )
    print(f"- Preserved answer-status warnings: {len(warning_ids)}")
    print(f"- Uncovered concepts: {sum(item['current_coverage_status'] != 'fully_covered' for item in coverage)}")
    print(f"- Errors: {len(errors)}")
    print(f"- Warnings: {len(warnings)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("PASS: all supplied questions have sufficient, source-labelled, non-leaking Study Library coverage.")


if __name__ == "__main__":
    main()
