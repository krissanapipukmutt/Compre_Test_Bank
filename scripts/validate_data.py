#!/usr/bin/env python3
"""Validate generated academic JSON and cross-references phase by phase."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)

    def warn(self, condition: bool, message: str) -> None:
        if not condition:
            self.warnings.append(message)


def load_json(path: Path, validation: Validation) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        validation.errors.append(f"missing JSON file: {path.relative_to(ROOT)}")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        validation.errors.append(f"invalid JSON/UTF-8 in {path.relative_to(ROOT)}: {exc}")
    return None


def unique(values: Iterable[str], label: str, validation: Validation) -> set[str]:
    sequence = list(values)
    found = set(sequence)
    validation.require(len(sequence) == len(found), f"duplicate {label} IDs detected")
    validation.require(all(bool(value) for value in sequence), f"blank {label} ID detected")
    return found


def path_id(rel_path: str) -> str:
    token = hashlib.sha256(unicodedata.normalize("NFC", rel_path).encode("utf-8")).hexdigest()[:16]
    return f"file-{token}"


def validate_phase_0(validation: Validation) -> None:
    payload = load_json(ROOT / "data/file-inventory.json", validation)
    if not isinstance(payload, dict):
        return
    files = payload.get("files")
    validation.require(isinstance(files, list), "inventory `files` must be a list")
    if not isinstance(files, list):
        return
    ids = unique((item.get("file_id") for item in files), "file", validation)
    rel_paths = unique((item.get("relative_path") for item in files), "relative-path", validation)
    validation.require(payload.get("source_file_count") == len(files), "source_file_count mismatch")
    validation.require(len(ids) == len(rel_paths), "file/path cardinality mismatch")

    discovered: list[Path] = []
    for directory in ("TERM1", "TERM2"):
        base = ROOT / directory
        if base.exists():
            discovered.extend(path for path in base.rglob("*") if path.is_file())
    for path in ROOT.iterdir():
        if path.is_file() and path.name not in {
            "AGENTS.md",
            "PLANS.md",
            "TASKS.md",
            "PROJECT_STATE.md",
            "README.md",
            ".DS_Store",
        } and path.suffix.lower() in {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".txt"}:
            discovered.append(path)
    if (ROOT / ".DS_Store").exists():
        discovered.append(ROOT / ".DS_Store")
    discovered_paths = {path.relative_to(ROOT).as_posix() for path in discovered}
    validation.require(rel_paths == discovered_paths, "inventory does not exactly match discovered source paths")

    required_fields = {
        "file_id",
        "relative_path",
        "filename",
        "extension",
        "size_bytes",
        "sha256",
        "detected_term",
        "detected_subject_code",
        "detected_subject_title",
        "classification_basis",
        "document_category",
        "apparent_version",
        "readable_status",
        "duplicate_status",
        "notes",
    }
    for item in files:
        missing = sorted(required_fields.difference(item))
        validation.require(not missing, f"{item.get('relative_path')} missing fields: {missing}")
        rel_path = item.get("relative_path")
        if not isinstance(rel_path, str):
            continue
        validation.require(item.get("file_id") == path_id(rel_path), f"unstable file ID for {rel_path}")
        path = ROOT / rel_path
        validation.require(path.is_file(), f"source missing: {rel_path}")
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            validation.require(digest == item.get("sha256"), f"source changed after inventory: {rel_path}")
            validation.require(path.stat().st_size == item.get("size_bytes"), f"size mismatch: {rel_path}")

    required_outputs = (
        "docs/00-file-inventory.md",
        "docs/01-course-mapping.md",
        "reports/phase-0-inventory-report.md",
        "reports/unreadable-files.md",
        "reports/duplicate-files.md",
        "reports/course-code-conflicts.md",
    )
    for output in required_outputs:
        validation.require((ROOT / output).is_file(), f"missing Phase 0 output: {output}")


def validate_phase_1(validation: Validation) -> None:
    subjects_payload = load_json(ROOT / "data/subjects.json", validation)
    chapters_payload = load_json(ROOT / "data/chapters.json", validation)
    topics_payload = load_json(ROOT / "data/topics.json", validation)
    glossary_payload = load_json(ROOT / "data/glossary.json", validation)
    refs_payload = load_json(ROOT / "data/source-references.json", validation)
    inventory = load_json(ROOT / "data/file-inventory.json", validation)
    if not all(isinstance(item, dict) for item in (subjects_payload, chapters_payload, topics_payload, glossary_payload, refs_payload, inventory)):
        return
    subjects = subjects_payload.get("subjects", [])
    chapters = chapters_payload.get("chapters", [])
    topics = topics_payload.get("topics", [])
    glossary = glossary_payload.get("glossary", [])
    refs = refs_payload.get("source_references", [])
    subject_ids = unique((item.get("subject_id") for item in subjects), "subject", validation)
    chapter_ids = unique((item.get("chapter_id") for item in chapters), "chapter", validation)
    topic_ids = unique((item.get("topic_id") for item in topics), "topic", validation)
    unique((item.get("glossary_id") for item in glossary), "glossary", validation)
    ref_ids = unique((item.get("source_reference_id") for item in refs), "source-reference", validation)
    file_ids = {item.get("file_id") for item in inventory.get("files", [])}
    for subject in subjects:
        validation.require(bool(subject.get("source_file_ids")), f"subject has no source: {subject.get('subject_id')}")
        validation.require(set(subject.get("source_file_ids", [])).issubset(file_ids), f"invalid source on subject {subject.get('subject_id')}")
    for chapter in chapters:
        validation.require(chapter.get("subject_id") in subject_ids, f"invalid subject on chapter {chapter.get('chapter_id')}")
        validation.require(set(chapter.get("source_reference_ids", [])).issubset(ref_ids), f"invalid source reference on chapter {chapter.get('chapter_id')}")
    for topic in topics:
        validation.require(topic.get("subject_id") in subject_ids, f"invalid subject on topic {topic.get('topic_id')}")
        validation.require(topic.get("chapter_id") in chapter_ids, f"invalid chapter on topic {topic.get('topic_id')}")
    for entry in glossary:
        validation.require(entry.get("subject_id") in subject_ids, f"invalid subject on glossary {entry.get('glossary_id')}")
        validation.require(entry.get("chapter_id") in chapter_ids, f"invalid chapter on glossary {entry.get('glossary_id')}")
    for ref in refs:
        validation.require(ref.get("file_id") in file_ids, f"invalid file on source reference {ref.get('source_reference_id')}")
    review_text = (ROOT / "reports/content-human-review.md").read_text(encoding="utf-8") if (ROOT / "reports/content-human-review.md").exists() else ""
    for collection, id_field in ((chapters, "chapter_id"), (topics, "topic_id"), (glossary, "glossary_id")):
        for item in collection:
            if item.get("confidence") == "low":
                validation.require(item.get(id_field, "") in review_text, f"low-confidence {id_field} missing from human-review report")


def validate_phase_2(validation: Validation) -> None:
    payload = load_json(ROOT / "data/questions.json", validation)
    subjects_payload = load_json(ROOT / "data/subjects.json", validation)
    chapters_payload = load_json(ROOT / "data/chapters.json", validation)
    topics_payload = load_json(ROOT / "data/topics.json", validation)
    inventory = load_json(ROOT / "data/file-inventory.json", validation)
    if not all(isinstance(item, dict) for item in (payload, subjects_payload, chapters_payload, topics_payload, inventory)):
        return
    questions = payload.get("questions", [])
    question_ids = unique((item.get("question_id") for item in questions), "question", validation)
    validation.require(len(question_ids) == len(questions), "question cardinality mismatch")
    subject_codes = {item.get("course_code") for item in subjects_payload.get("subjects", [])}
    chapter_ids = {item.get("chapter_id") for item in chapters_payload.get("chapters", [])}
    topic_ids = {item.get("topic_id") for item in topics_payload.get("topics", [])}
    file_ids = {item.get("file_id") for item in inventory.get("files", [])}
    review_text = (ROOT / "reports/exam-human-review.md").read_text(encoding="utf-8") if (ROOT / "reports/exam-human-review.md").exists() else ""
    required_bilingual = ("original_question_en", "question_th", "explanation_en", "explanation_th")
    for question in questions:
        qid = question.get("question_id")
        validation.require(question.get("source_exam_file_id") in file_ids, f"{qid}: invalid exam file")
        validation.require(question.get("subject_code") in subject_codes, f"{qid}: invalid subject")
        validation.require(question.get("chapter_id") in chapter_ids, f"{qid}: invalid chapter")
        validation.require(set(question.get("topic_ids", [])).issubset(topic_ids), f"{qid}: invalid topic")
        for field in required_bilingual:
            validation.require(bool(question.get(field)), f"{qid}: missing {field}")
        choices = question.get("choices", [])
        choice_ids = unique((item.get("choice_id") for item in choices), f"choice within {qid}", validation)
        answer = question.get("correct_answer")
        if isinstance(answer, list):
            validation.require(set(answer).issubset(choice_ids), f"{qid}: answer references invalid choice")
        elif answer is not None and choices:
            validation.require(answer in choice_ids, f"{qid}: answer references invalid choice")
        for choice in choices:
            validation.require(bool(choice.get("original_text_en")), f"{qid}: blank English choice")
            validation.require(bool(choice.get("text_th")), f"{qid}: blank Thai choice")
        if question.get("answer_status") in {
            "verified_from_source",
            "verified_from_course_material",
        }:
            validation.require(bool(question.get("source_references")), f"{qid}: verified answer lacks evidence")
        if question.get("answer_status") in {"ambiguous", "requires_human_review"}:
            validation.require(qid in review_text, f"{qid}: review item missing from exam report")


def validate_phase_7(validation: Validation) -> None:
    import subprocess

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_external_research.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    validation.require(
        result.returncode == 0,
        "Phase 7 external-research validation failed:\n" + result.stdout.strip(),
    )


def validate_phase_8(validation: Validation) -> None:
    import subprocess

    for script, label in (
        ("validate_exam_visual_integrity.py", "Phase 8 visual-integrity"),
        ("verify_final_question_visuals.py", "Final question-boundary"),
    ):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        validation.require(
            result.returncode == 0,
            f"{label} validation failed:\n" + result.stdout.strip(),
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", type=int, choices=(0, 1, 2, 3, 4, 5, 6, 7, 8), required=True)
    args = parser.parse_args()
    validation = Validation()
    validate_phase_0(validation)
    if args.phase >= 1:
        validate_phase_1(validation)
    if args.phase >= 2:
        validate_phase_2(validation)
    if args.phase >= 7:
        validate_phase_7(validation)
    if args.phase >= 8:
        validate_phase_8(validation)

    for warning in validation.warnings:
        print(f"WARNING: {warning}")
    for error in validation.errors:
        print(f"ERROR: {error}")
    print(
        f"Validation phase {args.phase}: "
        f"{'PASS' if not validation.errors else 'FAIL'} "
        f"({len(validation.errors)} errors, {len(validation.warnings)} warnings)"
    )
    return 1 if validation.errors else 0


if __name__ == "__main__":
    sys.exit(main())
