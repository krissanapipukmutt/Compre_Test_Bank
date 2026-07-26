#!/usr/bin/env python3
"""Validate Phase 8 examination visual assets, metadata, preservation, and gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tarfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

import fitz


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOT = ROOT / "web/public"
VISUAL_FIELDS = {
    "has_visual_content",
    "visual_integrity_status",
    "visual_content_position",
    "visual_assets",
    "original_layout_notes",
    "visual_extraction_method",
    "visual_review_note",
    "full_question_reference_asset",
    "source_page_dimensions",
    "visual_audit_completed_at",
    "visual_scoring_eligible",
}
TRANSLATION_FIELDS = {
    "question_th",
    "explanation_th",
    "original_explanation_th",
    "external_evidence_summary_th",
    "final_explanation_th",
    "confidence_rationale_th",
    "elimination_reasoning_th",
    "probability_warning_th",
    "remaining_uncertainty_th",
    "unresolved_reason_th",
    "translation_note",
    "translation_note_th",
    "translation_status",
    "translation_quality",
    "translation_review_note",
    "translation_completed_at",
    "translation_audit_log",
}
ALLOWED_STATUSES = {
    "complete",
    "repaired",
    "missing_visual",
    "partially_readable",
    "requires_human_review",
}
EXPECTED_VISUALS = {
    "question-comprehensive-021": (3, 34),
    "question-comprehensive-022": (3, 35),
    "question-comprehensive-023": (3, 36),
    "question-comprehensive-024": (3, 37),
    "question-comprehensive-062": (9, 56),
    "question-comprehensive-073": (10, 60),
    "question-comprehensive-077": (11, 64),
    "question-comprehensive-079": (12, 68),
    "question-comprehensive-080": (12, 69),
}
REQUIRED_REPORTS = {
    "exam-visual-integrity-audit.md",
    "missing-question-visuals.md",
    "repaired-question-visuals.md",
    "question-asset-extraction-log.md",
    "question-visual-human-review.md",
}


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def backup_questions() -> list[dict[str, Any]]:
    backups = sorted((ROOT / "backups").glob("pre-exam-visual-integrity-*.tar.gz"))
    if not backups:
        raise FileNotFoundError("No pre-exam-visual-integrity checkpoint exists")
    with tarfile.open(backups[-1], "r:gz") as archive:
        member = archive.extractfile("data/questions.json")
        if member is None:
            raise FileNotFoundError("Visual-integrity checkpoint has no data/questions.json")
        return json.loads(member.read().decode("utf-8"))["questions"]


def without_visual_fields(question: dict[str, Any]) -> dict[str, Any]:
    preserved = {
        key: value
        for key, value in question.items()
        if key not in VISUAL_FIELDS and key not in TRANSLATION_FIELDS
    }
    for field in ("choices", "original_choices"):
        if field not in preserved:
            continue
        preserved[field] = [
            {
                key: value
                for key, value in choice.items()
                if key
                not in {
                    "text_th",
                    "explanation_th",
                    "translation_status",
                    "translation_review_note",
                }
            }
            for choice in preserved[field]
        ]
    return preserved


def validate(check_build: bool) -> Checks:
    checks = Checks()
    payload = load("data/questions.json")
    web_payload = load("web/src/data/questions.json")
    audit = load("data/question-visual-audit.json")
    questions = payload.get("questions", [])
    originals = backup_questions()
    question_by_id = {question.get("question_id"): question for question in questions}
    original_by_id = {question.get("question_id"): question for question in originals}
    document = fitz.open(ROOT / "แนวข้อสอบ.pdf")
    asset_ids: set[str] = set()
    public_paths: set[str] = set()
    essential_asset_count = 0

    checks.require(payload == web_payload, "root and web question datasets differ")
    checks.require(len(question_by_id) == len(questions) == 105, "questions must contain 105 unique IDs")
    checks.require(set(question_by_id) == set(original_by_id), "question IDs changed from the Phase 8 checkpoint")
    checks.require(
        audit.get("source_exam_sha256") == sha256(ROOT / "แนวข้อสอบ.pdf"),
        "audit source hash does not match the immutable examination PDF",
    )

    for question_id, question in question_by_id.items():
        original = original_by_id[question_id]
        checks.require(
            without_visual_fields(question) == without_visual_fields(original),
            f"{question_id}: non-visual question data changed after the checkpoint",
        )
        missing_fields = sorted(VISUAL_FIELDS.difference(question))
        checks.require(not missing_fields, f"{question_id}: missing visual fields {missing_fields}")
        status = question.get("visual_integrity_status")
        checks.require(status in ALLOWED_STATUSES, f"{question_id}: invalid visual status {status}")
        eligible = status in {"complete", "repaired"}
        checks.require(
            question.get("visual_scoring_eligible") is eligible,
            f"{question_id}: visual scoring eligibility conflicts with status",
        )
        dimensions = question.get("source_page_dimensions", {})
        page_number = question.get("source_page_or_slide")
        checks.require(
            page_number == question.get("source_page_or_slide"),
            f"{question_id}: inconsistent source page",
        )
        if isinstance(page_number, int) and 1 <= page_number <= len(document):
            page = document[page_number - 1]
            checks.require(
                dimensions == {
                    "width": round(page.rect.width, 2),
                    "height": round(page.rect.height, 2),
                    "unit": "points",
                },
                f"{question_id}: source-page dimensions do not match the PDF",
            )
        assets = question.get("visual_assets")
        checks.require(isinstance(assets, list), f"{question_id}: visual_assets must be a list")
        if not isinstance(assets, list):
            continue
        essential = [asset for asset in assets if asset.get("is_essential") is True]
        has_visual = question.get("has_visual_content") is True
        checks.require(
            not has_visual or not eligible or bool(essential),
            f"{question_id}: score-eligible visual question lacks an essential asset",
        )
        checks.require(
            has_visual == (question_id in EXPECTED_VISUALS),
            f"{question_id}: original visual classification differs from the manual audit",
        )
        if question_id in EXPECTED_VISUALS:
            expected_page, expected_xref = EXPECTED_VISUALS[question_id]
            checks.require(status == "repaired", f"{question_id}: expected repaired status")
            checks.require(len(essential) == 1, f"{question_id}: expected one essential inline asset")
            checks.require(
                question.get("full_question_reference_asset")
                == next(
                    (
                        asset.get("public_path")
                        for asset in assets
                        if asset.get("placement") == "full_question_reference"
                    ),
                    None,
                ),
                f"{question_id}: full-question reference linkage is invalid",
            )
            if essential:
                checks.require(
                    essential[0].get("source_page") == expected_page
                    and essential[0].get("source_object_xref") == expected_xref,
                    f"{question_id}: source object locator differs from the audited PDF",
                )
        else:
            checks.require(status == "complete", f"{question_id}: text-only question is not complete")
            checks.require(not assets, f"{question_id}: text-only question unexpectedly has assets")

        for asset in assets:
            asset_id = asset.get("asset_id")
            checks.require(
                isinstance(asset_id, str) and asset_id not in asset_ids,
                f"{question_id}: duplicate or invalid asset ID {asset_id}",
            )
            if isinstance(asset_id, str):
                asset_ids.add(asset_id)
            public_path = asset.get("public_path")
            checks.require(isinstance(public_path, str), f"{question_id}: invalid public asset path")
            if not isinstance(public_path, str):
                continue
            checks.require(
                asset.get("path") == public_path,
                f"{question_id}: asset path/public_path mismatch",
            )
            checks.require(
                asset.get("source_file_id") == question.get("source_exam_file_id"),
                f"{question_id}: asset source file is invalid",
            )
            checks.require(
                asset.get("source_page_or_slide") == question.get("source_page_or_slide")
                == asset.get("source_page"),
                f"{question_id}: asset source page is invalid",
            )
            posix = PurePosixPath(public_path)
            checks.require(
                public_path.startswith("/exam-assets/")
                and ".." not in posix.parts
                and "\\" not in public_path,
                f"{question_id}: unsafe asset path {public_path}",
            )
            checks.require(public_path not in public_paths, f"{question_id}: duplicate asset path")
            public_paths.add(public_path)
            asset_path = PUBLIC_ROOT / public_path.lstrip("/")
            checks.require(asset_path.is_file(), f"{question_id}: missing asset {public_path}")
            if not asset_path.is_file():
                continue
            checks.require(sha256(asset_path) == asset.get("sha256"), f"{question_id}: asset hash mismatch")
            try:
                pixmap = fitz.Pixmap(asset_path)
                checks.require(
                    (pixmap.width, pixmap.height)
                    == (asset.get("width"), asset.get("height")),
                    f"{question_id}: asset dimensions mismatch for {public_path}",
                )
            except RuntimeError as exc:
                checks.errors.append(f"{question_id}: unreadable asset {public_path}: {exc}")
            checks.require(bool(asset.get("alt_en")) and bool(asset.get("alt_th")), f"{question_id}: bilingual alt text is required")
            checks.require(
                asset.get("placement")
                in {
                    "after_translation_before_choices",
                    "within_choice",
                    "full_question_reference",
                },
                f"{question_id}: invalid asset placement",
            )
            bbox = asset.get("source_bbox", {})
            checks.require(
                all(isinstance(bbox.get(key), (int, float)) for key in ("x", "y", "width", "height"))
                and bbox.get("x", -1) >= 0
                and bbox.get("y", -1) >= 0
                and bbox.get("width", 0) > 0
                and bbox.get("height", 0) > 0
                and bbox.get("x", 0) + bbox.get("width", 0) <= dimensions.get("width", 0) + 0.1
                and bbox.get("y", 0) + bbox.get("height", 0) <= dimensions.get("height", 0) + 0.1,
                f"{question_id}: source crop is outside page bounds",
            )
            answer_texts = [
                choice.get("original_text_en", "").strip().lower()
                for choice in question.get("choices", [])
                if choice.get("choice_id") == question.get("correct_answer")
            ]
            descriptive_text = " ".join(
                str(asset.get(key, "")).lower()
                for key in ("public_path", "alt_en", "alt_th", "caption_en", "caption_th")
            )
            for answer_text in answer_texts:
                if len(answer_text) >= 8:
                    checks.require(
                        answer_text not in descriptive_text,
                        f"{question_id}: visual metadata leaks the answer text",
                    )
            if asset.get("is_essential") is True:
                essential_asset_count += 1
                xref = asset.get("source_object_xref")
                checks.require(isinstance(xref, int), f"{question_id}: essential asset lacks source xref")
                if isinstance(xref, int):
                    original_bytes = document.extract_image(xref)["image"]
                    checks.require(
                        hashlib.sha256(original_bytes).hexdigest() == sha256(asset_path),
                        f"{question_id}: inline asset bytes differ from the embedded original",
                    )
            else:
                checks.require(
                    asset.get("placement") == "full_question_reference",
                    f"{question_id}: non-essential asset is not a reference image",
                )
            if check_build:
                build_path = ROOT / "web/dist" / public_path.lstrip("/")
                checks.require(build_path.is_file(), f"{question_id}: asset missing from production build")
                if build_path.is_file():
                    checks.require(
                        sha256(build_path) == sha256(asset_path),
                        f"{question_id}: production asset differs from canonical public asset",
                    )

    counts = Counter(question.get("visual_integrity_status") for question in questions)
    checks.require(
        counts == Counter({"complete": 96, "repaired": 9}),
        f"unexpected visual status counts: {dict(counts)}",
    )
    checks.require(essential_asset_count == 9, "expected exactly nine essential visual assets")
    checks.require(len(asset_ids) == 18, "expected exactly 18 unique source assets")
    checks.require(
        audit.get("summary")
        == {
            "total_questions": 105,
            "text_only_complete": 96,
            "visual_questions_repaired": 9,
            "missing": 0,
            "partial": 0,
            "requires_human_review": 0,
            "assets_extracted": 18,
        },
        "visual audit summary is inconsistent",
    )
    audit_ids = [item.get("question_id") for item in audit.get("questions", [])]
    checks.require(
        len(audit_ids) == len(set(audit_ids)) == 105
        and set(audit_ids) == set(question_by_id),
        "visual audit does not cover every question exactly once",
    )
    for report in REQUIRED_REPORTS:
        path = ROOT / "reports" / report
        checks.require(path.is_file() and path.stat().st_size > 100, f"missing or empty report: {report}")

    engine_source = (ROOT / "web/src/engine.ts").read_text(encoding="utf-8")
    session_source = (ROOT / "web/src/session.ts").read_text(encoding="utf-8")
    checks.require(
        "!isVisualReady(question)" in engine_source,
        "scoreQuestion does not exclude visually incomplete questions",
    )
    checks.require(
        "isVisualReady(question)" in session_source,
        "mock-session selection does not require visual readiness",
    )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-build", action="store_true")
    args = parser.parse_args()
    checks = validate(args.check_build)
    for warning in checks.warnings:
        print(f"WARNING: {warning}")
    for error in checks.errors:
        print(f"ERROR: {error}")
    print(
        "Phase 8 examination visual-integrity validation: "
        f"{'PASS' if not checks.errors else 'FAIL'} "
        f"({len(checks.errors)} errors, {len(checks.warnings)} warnings)"
    )
    return 1 if checks.errors else 0


if __name__ == "__main__":
    sys.exit(main())
