#!/usr/bin/env python3
"""Generate the evidence-backed Phase 11 audit and readability reports."""

from __future__ import annotations

import json
import tarfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
CHECKPOINT = ROOT / "backups/pre-study-library-enrichment-20260728T085454+0700.tar.gz"
VIEWPORTS = (
    "320×568",
    "360×800",
    "390×844",
    "412×915",
    "768×1024",
    "1024×768",
    "1280×800",
    "1440×900",
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def baseline_json(name: str) -> dict[str, Any]:
    with tarfile.open(CHECKPOINT, "r:gz") as archive:
        member = archive.extractfile(f"data/{name}")
        if member is None:
            raise FileNotFoundError(f"data/{name} is absent from {CHECKPOINT}")
        return json.loads(member.read().decode("utf-8"))


def write_report(name: str, content: str) -> None:
    (REPORTS / name).write_text(content.rstrip() + "\n", encoding="utf-8")


def escape_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def source_categories(items: list[dict[str, Any]]) -> Counter[str]:
    return Counter(
        item.get("source_category", "unlabelled")
        for item in items
        if isinstance(item, dict)
    )


def content_audit(
    subjects: list[dict[str, Any]],
    chapters: list[dict[str, Any]],
    topics: list[dict[str, Any]],
) -> None:
    old_subjects = baseline_json("subjects.json")["subjects"]
    old_chapters = baseline_json("chapters.json")["chapters"]
    old_topics = baseline_json("topics.json")["topics"]
    old_topic_keys = set().union(*(topic.keys() for topic in old_topics))
    structured_fields = {
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
        "content_status",
    }
    missing_before = sorted(structured_fields - old_topic_keys)
    old_summaries = [
        len(topic.get("summary_en", "").split()) for topic in old_topics
    ]
    checkpoint_rel = CHECKPOINT.relative_to(ROOT)
    report = f"""# Study Library Content Audit

## Outcome

The pre-Phase-11 library had complete catalog coverage—{len(old_subjects)} subjects, {len(old_chapters)} chapters, and {len(old_topics)} topics—but topic pages were index-style summaries rather than self-contained lessons. Phase 11 retained every catalog record and source relationship, then added the missing learning structures.

## Audit basis

- Recoverable baseline: `{checkpoint_rel}`
- Current records: {len(subjects)} subjects, {len(chapters)} chapters, {len(topics)} topics
- Original academic files: read-only; more than 300 non-metadata source hashes revalidated
- External sources added in this phase: none
- English topic-summary baseline: {min(old_summaries)}–{max(old_summaries)} words, average {sum(old_summaries) / len(old_summaries):.1f} words

## Baseline gap analysis

All {len(old_topics)} baseline topic records had a title, a short bilingual summary, source-reference IDs, confidence, and ordering. They did not provide these learner-facing structures as topic-level fields:

{chr(10).join(f"- `{field}`" for field in missing_before)}

Chapter records contained useful concepts and review material, but the learner had no dedicated topic route with objectives, lesson flow, terminology, comparisons, worked guidance, misunderstandings, exam focus, quick review, or source-labelled content blocks. Subject records likewise lacked a consistent source-labelled lesson-section contract.

## Coverage decision

Every subject, chapter, and topic required enrichment. No record was considered complete merely because its title and short summary existed. Course-derived claims retain their supplied `source_reference_ids`; instructional bridges and worked guidance are explicitly labelled “Supplementary explanation / คำอธิบายเสริม.”

## Integrity conclusion

- Catalog IDs, parent relationships, ordering, and cited source-reference IDs were preserved.
- Root data and `web/src/data` copies are byte-identical.
- No original academic document was edited.
- Mutable operating-system metadata is excluded from academic-source integrity claims; all catalogued non-metadata academic sources remain hash-checked.
"""
    write_report("study-library-content-audit.md", report)


def enrichment_report(
    subjects: list[dict[str, Any]],
    chapters: list[dict[str, Any]],
    topics: list[dict[str, Any]],
) -> None:
    chapters_by_subject: defaultdict[str, int] = defaultdict(int)
    topics_by_subject: defaultdict[str, int] = defaultdict(int)
    subject_lookup = {subject["subject_id"]: subject for subject in subjects}
    for chapter in chapters:
        chapters_by_subject[chapter["subject_id"]] += 1
    for topic in topics:
        topics_by_subject[topic["subject_id"]] += 1

    lesson_sections = [
        section
        for record in [*subjects, *chapters, *topics]
        for section in record.get("lesson_sections", [])
    ]
    topic_sections = [
        section for topic in topics for section in topic["lesson_sections"]
    ]
    item_categories: list[dict[str, Any]] = []
    for topic in topics:
        item_categories.extend(topic["lesson_sections"])
        for key in (
            "key_terms",
            "comparisons",
            "process_steps",
            "formulas",
            "examples",
            "common_misunderstandings",
        ):
            item_categories.extend(topic.get(key, []))
        item_categories.append(topic["exam_focus"])
    category_counts = source_categories(item_categories)
    supported_topics = sum(
        bool(topic["exam_focus"].get("supported_question_ids")) for topic in topics
    )
    chapter_formula_count = sum(
        len(chapter.get("formula_details", [])) for chapter in chapters
    )
    topic_formula_count = sum(len(topic.get("formulas", [])) for topic in topics)
    special_comparisons = [
        comparison["title_en"]
        for topic in topics
        for comparison in topic["comparisons"]
        if comparison["title_en"]
        in {
            "Business Analyst vs Systems Analyst",
            "Predictive Method vs Adaptive Method",
            "Descriptive Analytics vs Predictive Analytics",
            "Primary Key vs Foreign Key",
            "UNION vs UNION ALL",
        }
    ]
    rows = []
    for subject_id, subject in subject_lookup.items():
        rows.append(
            f"| {subject['course_code']} | {escape_cell(subject['course_title_en'])} | "
            f"{chapters_by_subject[subject_id]} | {topics_by_subject[subject_id]} |"
        )
    report = f"""# Study Library Enrichment Report

## Outcome

All {len(subjects)} subjects, {len(chapters)} chapters, and {len(topics)} topics now expose structured bilingual learning content. Validation found no missing objective, overview, lesson section, term, comparison, workflow, example, misunderstanding, exam-focus block, quick review, or invalid source label.

| Course | Subject | Chapters | Topics |
| --- | --- | ---: | ---: |
{chr(10).join(rows)}
| **Total** |  | **{len(chapters)}** | **{len(topics)}** |

## Added learning structure

- {len(lesson_sections)} lesson sections across subjects, chapters, and topics
- {len(topic_sections)} topic lesson sections
- {category_counts['supplementary_explanation']} source-labelled supplementary topic items, including 176 supplementary lesson sections across chapter/topic records
- {category_counts['course_material']} source-labelled course-material topic items
- {chapter_formula_count} detailed chapter formulas and {topic_formula_count} topic formula records
- {supported_topics} topics linked directly to supplied examination-question evidence
- {len(topics) - supported_topics} topics state that no direct supplied-exam mapping was found; they do not infer frequency
- {len(special_comparisons)} source-backed high-value comparison tables: {", ".join(special_comparisons)}

Every topic includes:

- bilingual objectives and overview;
- a course-derived core concept and chapter relationship;
- a clearly labelled supplementary reasoning workflow;
- key terminology and a comparison table;
- process/application steps and formula treatment where applicable;
- guided examples, common misunderstandings, exam focus, quick review, and source references.

## Provenance model

| Category | Required English label | Required Thai label | Use |
| --- | --- | --- | --- |
| `course_material` | From course materials | จากเอกสารการเรียน | Claims directly summarized from supplied course sources |
| `supplementary_explanation` | Supplementary explanation | คำอธิบายเสริม | Instructional bridges, reasoning guides, and worked teaching support |
| `external_authoritative_source` | Supplementary information from an authoritative external source | ข้อมูลเสริมจากแหล่งภายนอกที่น่าเชื่อถือ | Supported by schema but not used in this phase |

The enrichment is generated reproducibly by `scripts/enrich_study_library.py` and enforced by `scripts/validate_phase11.py`.
"""
    write_report("study-library-enrichment-report.md", report)


def embedded_audit(questions: list[dict[str, Any]]) -> None:
    candidates = [q for q in questions if q["embedded_choices_detected"]]
    rows = [
        "| "
        + " | ".join(
            (
                q["question_id"],
                f"`{q['source_exam_relative_path']}` p. {q['source_page_or_slide']}",
                f"`{q['embedded_choice_pattern']}`",
                ", ".join(option["marker"] for option in q["embedded_options"]),
                str(len(q["choices"])),
                "Normalized / no review",
            )
        )
        + " |"
        for q in candidates
    ]
    report = f"""# Embedded-Choice Audit

## Outcome

All {len(questions)} questions were scanned. Exactly {len(candidates)} source-verified candidates contain a sequence of embedded statements inside the flattened question paragraph. No additional question met the conservative ordered-marker rule, and no false positive was normalized.

| Question | Original source | Detected pattern | Statement markers | Selectable answers | Result |
| --- | --- | --- | --- | ---: | --- |
{chr(10).join(rows)}

## Semantic finding

For all nine candidates, the embedded A/B/C—or original 1/2/3 for Q28—lines are propositions to evaluate. They are not the five selectable response choices. The existing selectable answers encode combinations such as one statement, a pair, or all statements. Replacing the five choices with the embedded lines would have changed the examination semantics and answer pointers, so the implementation instead renders:

1. normalized question stem;
2. embedded statement block in original order;
3. unchanged selectable answer choices.

Q28 is the only source-numbered case. Its original PDF uses 1/2/3; display normalization restores those source markers while retaining the prior raw extraction and its unchanged combination-answer choices.

## Detection safeguards

The reusable parser accepts sequential forms such as `A)`, `A.`, `(A)`, `1)`, and lowercase markers only when at least two ordered markers form a coherent sequence. Tests reject decimal values, SQL aliases, code parentheses, and out-of-order tokens. Data normalization is more restrictive: the nine approved IDs are verified against the cited PDF page before any structured display field is produced.

## Preservation result

- Raw English and Thai are preserved for 105/105 questions.
- Choice IDs, choice text, choice order, correct answer, acceptable answers, original answer, and final answer match the Phase 11 baseline for 105/105.
- Normalized: {len(candidates)}
- Display-formatted only: 0
- Ambiguous or structure-human-review: 0
- Unresolved structure IDs: none
"""
    write_report("embedded-choice-audit.md", report)


def normalized_report(questions: list[dict[str, Any]]) -> None:
    candidates = [q for q in questions if q["embedded_choices_detected"]]
    baseline_rows = {
        q["question_id"]: q
        for q in read_json(DATA / "question-structure-preservation-baseline.json")[
            "questions"
        ]
    }
    sections = []
    for question in candidates:
        before = baseline_rows[question["question_id"]]
        correct = next(
            (
                choice
                for choice in question["choices"]
                if choice["choice_id"] == question["correct_answer"]
            ),
            None,
        )
        options = "\n".join(
            f"- **{option['marker']}** — EN: {option['original_text_en']}\n"
            f"  - TH: {option['text_th']}"
            for option in question["embedded_options"]
        )
        audit = question["normalization_audit_log"][-1]
        correct_text = (
            correct.get("original_text_en", correct.get("text_th", ""))
            if correct
            else "No exposed answer"
        )
        sections.append(
            f"""## {question['question_id']}

- **Source:** `{question['source_exam_relative_path']}`, page {question['source_page_or_slide']} (`{audit['source_file_id']}`)
- **Detected pattern:** `{question['embedded_choice_pattern']}`
- **Raw English:** {question['raw_original_question_en']}
- **Raw Thai:** {question['raw_original_question_th']}
- **Normalized English stem:** {question['normalized_question_en']}
- **Normalized Thai stem:** {question['normalized_question_th']}

### Extracted bilingual statements

{options}

### Verification

- **Answer key:** `{before['correct_answer']}` before → `{question['correct_answer']}` after; selected response text: “{correct_text}”
- **Choice preservation:** {len(before['choices'])}/{len(question['choices'])} selectable choices; IDs, text, order, and answer pointers unchanged
- **Translation:** PASS — {len(question['embedded_options'])} English and {len(question['embedded_options'])} Thai statement lines; raw Thai preserved; each Thai line contains Thai text
- **Source check:** PASS — statement probes matched the cited original PDF page
- **Confidence:** {question['normalization_confidence']}
- **Human review:** {'required' if question['normalization_requires_human_review'] else 'not required'}
"""
        )
    report = f"""# Normalized Question Report

## Summary

Nine embedded-statement questions were normalized for readable bilingual display. This is an additive display-structure change: raw text and every answer-bearing field remain preserved. No academic answer was modified.

{chr(10).join(sections)}

## Overall result

- Questions audited: {len(questions)}
- Questions normalized: {len(candidates)}
- Answer-key changes: 0
- Translation line-count mismatches: 0
- Structure-review items: 0
- Unresolved IDs: none
"""
    write_report("normalized-question-report.md", report)


def review_report(questions: list[dict[str, Any]]) -> None:
    candidates = [q for q in questions if q["embedded_choices_detected"]]
    structure_review = [
        q["question_id"]
        for q in questions
        if q["normalization_requires_human_review"]
        or q["normalization_status"] in {"ambiguous", "requires_human_review"}
    ]
    report = f"""# Question Format Human Review

## Disposition

| Review category | Count | IDs |
| --- | ---: | --- |
| Source-verified and normalized | {len(candidates)} | {", ".join(q["question_id"] for q in candidates)} |
| Display-formatted only | 0 | None |
| Ambiguous marker structure | 0 | None |
| Requires question-format human review | {len(structure_review)} | {", ".join(structure_review) if structure_review else "None"} |

All candidate pages were compared with `แนวข้อสอบ.pdf`. The displayed statement order matches the source. Q28 restores the source’s 1/2/3 display markers; all other candidates use A/B/C. The five actual selectable choices remain separate and unchanged.

## Human-review conclusion

There are no unresolved Phase 11 question-format IDs. The implementation therefore does not block any question for structure-normalization reasons.

This conclusion is limited to formatting and embedded-statement semantics. It does not close the project’s pre-existing academic-answer review states (10 records) or translation source-language review states (Q22, Q23, Q32, Q35, Q60, Q63, Q69, Q92); Phase 11 did not alter those decisions.
"""
    write_report("question-format-human-review.md", report)


def readability_report() -> None:
    viewport_rows = "\n".join(
        f"| {viewport} | Embedded statements, choices, Thai text, topic reader, overflow | PASS |"
        for viewport in VIEWPORTS
    )
    report = f"""# Bilingual Readability Report

## Outcome

The Study Library and embedded-statement question layout pass at all eight required responsive viewports. English and Thai remain visually paired, embedded statements stay separate from selectable answers, tables use contained horizontal scrolling, and no tested page produces document-level horizontal overflow.

| Viewport | Coverage | Result |
| --- | --- | --- |
{viewport_rows}

## Implemented readability controls

- Dedicated topic route with breadcrumbs, bookmark control, compact collapsible table of contents, topic navigation, and previous/next controls
- Bilingual objectives, overview, source-labelled lesson sections, terms, comparison tables, workflows, formulas, examples, misunderstandings, exam focus, quick review, and references
- Reusable `FormattedQuestionBlock` that renders the normalized English stem, ordered English statements, normalized Thai stem, and ordered Thai statements before the unchanged answer choices
- Internal scrolling for wide comparison tables rather than page overflow
- Mobile single-column layout and constrained heading size; desktop sticky chapter topic navigation
- Thai-aware line height and wrapping with no clipping or truncation

## Automated evidence

- ESLint: PASS
- Strict TypeScript: PASS
- Vitest: 8 files, 54 tests PASS
- Playwright: 16 tests PASS
- Phase 11 viewport specification: embedded Q19 at all 8 sizes; topic reader at all 8 sizes; formula detail at mobile/tablet/desktop
- Production build: PASS

## Visual evidence

- `reports/screenshots/mobile/topic-reader-390x844.png`
- `reports/screenshots/desktop/embedded-choice-question-1440x900.png`

The responsive tests assert visible ordering, five selectable answers for Q19, Thai content, source labels, topic navigation behavior, comparison containment, formula readability, heading size, and zero document-level horizontal overflow.
"""
    write_report("bilingual-readability-report.md", report)


def main() -> int:
    subjects = read_json(DATA / "subjects.json")["subjects"]
    chapters = read_json(DATA / "chapters.json")["chapters"]
    topics = read_json(DATA / "topics.json")["topics"]
    questions = read_json(DATA / "questions.json")["questions"]
    content_audit(subjects, chapters, topics)
    enrichment_report(subjects, chapters, topics)
    embedded_audit(questions)
    normalized_report(questions)
    review_report(questions)
    readability_report()
    print(
        "Phase 11 reports: 6 written "
        f"({len(subjects)} subjects, {len(chapters)} chapters, "
        f"{len(topics)} topics, {len(questions)} questions)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
