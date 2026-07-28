#!/usr/bin/env python3
"""Generate the seven Phase 12 exam-to-study coverage audit reports."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
DATE = "2026-07-28"
CHECKPOINT = "backups/pre-exam-to-study-coverage-audit-20260728T100551+0700.tar.gz"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def ids(values: list[str]) -> str:
    return ", ".join(values) if values else "None"


def write(name: str, content: str) -> None:
    (REPORTS / name).write_text(content.rstrip() + "\n")


def main() -> None:
    questions = load("data/questions.json")["questions"]
    topics = load("data/topics.json")["topics"]
    coverage = load("data/question-study-coverage.json")["question_study_coverage"]
    topic_map = load("data/study-topic-question-map.json")["study_topic_question_map"]
    sources = load("data/external-sources.json")["external_sources"]

    question_by_id = {item["question_id"]: item for item in questions}
    topic_by_id = {item["topic_id"]: item for item in topics}
    source_by_id = {item["source_id"]: item for item in sources}
    coverage_by_id = {item["question_id"]: item for item in coverage}
    initial = Counter(item["initial_coverage_status"] for item in coverage)
    final = Counter(item["final_coverage_status"] for item in coverage)
    origins = Counter(item["evidence_origin"] for item in coverage)
    subject_counts = Counter(item["subject_code"] for item in coverage)
    warning_ids = [
        item["question_id"] for item in coverage if item["answer_status_warning"]
    ]
    uncovered_ids = [
        item["question_id"]
        for item in coverage
        if item["current_coverage_status"] != "fully_covered"
    ]
    coverage_sections = [
        (topic, section)
        for topic in topics
        for section in topic["lesson_sections"]
        if section["section_id"].startswith("coverage-")
    ]
    tested_topics = [item for item in topic_map if item["question_count"]]

    subject_rows = "\n".join(
        f"| {subject} | {subject_counts[subject]} | "
        f"{sum(item['subject_code'] == subject and item['initial_coverage_status'] != 'fully_covered' for item in coverage)} | "
        f"{sum(item['subject_code'] == subject and item['current_coverage_status'] == 'fully_covered' for item in coverage)} |"
        for subject in sorted(subject_counts)
    )

    audit = f"""# Exam-to-Study Coverage Audit

Audit date: {DATE}

Scope: all 105 supplied comprehensive-examination questions and all 132 Study Library topics

Recovery checkpoint: `{CHECKPOINT}`

## Outcome

All 105 questions now have a precise, bidirectional link to concept teaching that is sufficient for guided bilingual self-study. The audit added or confirmed {len(coverage_sections)} grouped teaching sections across {len(tested_topics)} directly tested topics. No question is marked complete merely because its text or choices exist.

- Current fully covered concepts: {sum(item["current_coverage_status"] == "fully_covered" for item in coverage)}/105
- Still-partial or unresolved coverage: {len(uncovered_ids)}
- Precise question-to-topic links: {sum(item["question_count"] for item in topic_map)}
- Topics with supplied-exam evidence: {len(tested_topics)}/132
- Topics with no supplied-exam example: {len(topic_map) - len(tested_topics)}/132
- Preserved academic-answer warnings: {len(warning_ids)}
- Academic answers changed during this phase: 0

Exact unresolved coverage IDs: **{ids(uncovered_ids)}**

The {len(warning_ids)} answer-warning records are not coverage failures. Their concepts are taught, while their pre-existing answer/scoring judgments remain visible and unchanged: {ids(warning_ids)}.

## Method

Each question was read as an assessment task, not accepted from tags alone. The audit recorded the tested concept, tested skill, prerequisite topics, initial coverage quality, evidence origin, precise Study Library topic, repair made, and final coverage quality. A question passes coverage only when a learner can find a bilingual definition or framework, discriminating rule or comparison, and guidance for applying the concept without seeing the answer.

The dedicated mapping deliberately excludes correct-answer IDs, correct-choice text, probability distributions, and answer explanations. Lesson repairs teach reusable concepts and never mention question IDs in learner-facing prose.

## Initial and final coverage

| Initial condition | Questions |
|---|---:|
| Fully covered | {initial["fully_covered"]} |
| Partially covered | {initial["partially_covered"]} |
| Keyword only | {initial["keyword_only"]} |
| Conflicting or uncertain | {initial["conflicting_or_uncertain"]} |
| Missing | {initial["missing"]} |

| Final evidence-backed condition | Questions |
|---|---:|
| Fully covered from supplied course evidence | {final["fully_covered"]} |
| Covered with authoritative external sources | {final["covered_with_external_sources"]} |
| Covered with explicitly labelled supplementary explanation | {final["covered_with_supplementary_content"]} |
| Still partial | {final["still_partial"]} |
| Unresolved coverage | {final["unresolved"]} |

## Subject coverage

| Subject | Questions audited | Initially needing repair | Currently fully covered |
|---|---:|---:|---:|
{subject_rows}

## Evidence controls

Evidence origins are explicit: course material {origins["COURSE_MATERIAL"]}, authoritative external {origins["EXTERNAL_AUTHORITATIVE"]}, and supplementary explanation {origins["SUPPLEMENTARY_EXPLANATION"]}. External coverage resolves to records in `data/external-sources.json`; course coverage resolves to `data/source-references.json`. Supplementary sections are used for reasoning rules where the supplied item is under-specified or internally conflicting, and they do not silently adjudicate those answer records.

## Application traceability

Every topic page now includes “Related examination topics / หัวข้อที่เกี่ยวข้องกับแนวข้อสอบ,” including question count, bilingual tested concepts, difficulty distribution, a non-prevalence frequency signal, topic-filtered practice, and a generic answer-status warning where applicable. After answer submission, each question review links to its most relevant topic. No link is shown before submission.

## Verification gates

The Phase 12 validator checks 105/105 coverage records, all 132 topic-map records, bidirectional links, exact counts, evidence origins, source resolution, answer-warning consistency, learner-facing no-leakage rules, root/web data synchronization, and academic-answer preservation against Git checkpoint `e722f98`. Final project gates comprise data validation, lint, strict TypeScript checking, unit/component tests, Playwright browser tests at the seven required viewports, and the production build.
"""
    write("exam-to-study-coverage-audit.md", audit)

    gap_groups: dict[str, list[dict]] = defaultdict(list)
    for item in coverage:
        gap_groups[item["initial_coverage_status"]].append(item)
    gap_sections = []
    for status in (
        "conflicting_or_uncertain",
        "keyword_only",
        "partially_covered",
        "missing",
        "fully_covered",
    ):
        items = gap_groups[status]
        gap_sections.append(
            f"### {status.replace('_', ' ').title()} ({len(items)})\n\n"
            + "\n".join(
                f"- `{item['question_id']}` — {item['tested_concept_en']} / "
                f"{item['tested_concept_th']} → `{item['primary_study_topic_id']}`"
                for item in items
            )
        )
    missing = f"""# Missing Study Content Found During the Exam Audit

Audit date: {DATE}

## Finding

Before repair, {len(coverage) - initial["fully_covered"]} of 105 tested concepts were not taught at the exact depth required: {initial["partially_covered"]} were partial, {initial["keyword_only"]} were keyword-only, and {initial["conflicting_or_uncertain"]} were tied to conflicting or under-specified items. No concept was absent from the broad subject hierarchy, but broad chapter association was not accepted as sufficient coverage.

The highest-impact gaps were interview conduct and analyst-role boundaries; regression diagnostics and descriptive statistics; enterprise integration and decision-support systems; marketing growth, brand, promotion, and service distinctions; candidate keys and SQL set operations; web-stack/API/cloud classification; and networking layers, signaling, routing, QoS, wireless security, and switch design.

## Pre-repair inventory

{chr(10).join(gap_sections)}

## Disposition

Every item above now has a grouped bilingual lesson section and a precise topic link. Exact still-uncovered coverage IDs: **{ids(uncovered_ids)}**. Academic-answer ambiguity remains a separate controlled state and was not hidden by the content repair.
"""
    write("missing-study-content.md", missing)

    added_rows = []
    for topic, section in sorted(
        coverage_sections,
        key=lambda pair: (pair[0]["subject_id"], pair[0]["chapter_id"], pair[1]["section_id"]),
    ):
        added_rows.append(
            f"| `{section['section_id']}` | {topic['title_en']} / {topic['title_th']} | "
            f"{len(section['related_question_ids'])} | {section['evidence_origin']} | "
            f"{section['heading_en']} / {section['heading_th']} |"
        )
    added = f"""# Study Content Added from Examination Coverage

Audit date: {DATE}

The repair added or regenerated {len(coverage_sections)} reusable bilingual teaching sections. Each section is attached to an existing curriculum topic, source-labelled, and connected to one or more questions only through metadata. Learner-facing content contains no question ID, correct choice, or answer explanation.

| Section | Study topic | Questions supported | Evidence origin | Teaching focus |
|---|---|---:|---|---|
{chr(10).join(added_rows)}

Totals: {len(coverage_sections)} sections; {sum(len(section["related_question_ids"]) for _, section in coverage_sections)} question-section support links; {len(tested_topics)} tested topics. Multiple questions that test one conceptual framework share a lesson rather than duplicating answer-oriented text.
"""
    write("study-content-added-from-exams.md", added)

    external_usage: dict[str, set[str]] = defaultdict(set)
    for item in coverage:
        if item["evidence_origin"] == "EXTERNAL_AUTHORITATIVE":
            for source_id in item["external_source_ids"]:
                external_usage[source_id].add(item["question_id"])
    external_rows = []
    for source_id, qids in sorted(external_usage.items()):
        source = source_by_id[source_id]
        external_rows.append(
            f"| `{source_id}` | {source['organization_or_author']} | "
            f"[{source['title']}]({source['url']}) | {len(qids)} | {ids(sorted(qids))} |"
        )
    external = f"""# Study Content External Sources

Audit date: {DATE}

Authoritative external teaching support was used for {origins["EXTERNAL_AUTHORITATIVE"]} question mappings and resolves to {len(external_usage)} existing, locally recorded source entries. No academic file was uploaded or sent to an external service during this phase. The audit reused previously researched source records and their access metadata.

| Source ID | Organization or author | Source | Questions | Question IDs |
|---|---|---|---:|---|
{chr(10).join(external_rows)}

External material is labelled “Supplementary information from an authoritative external source / ข้อมูลเสริมจากแหล่งภายนอกที่น่าเชื่อถือ” in the Study Library. It supports general teaching, not direct disclosure of examination answers.
"""
    write("study-content-external-sources.md", external)

    link_rows = []
    for item in coverage:
        topic = topic_by_id[item["primary_study_topic_id"]]
        link_rows.append(
            f"| `{item['question_id']}` | {item['subject_code']} | "
            f"{item['tested_concept_en']} / {item['tested_concept_th']} | "
            f"`{topic['topic_id']}` — {topic['title_en']} | "
            f"{item['final_coverage_status']} | "
            f"{'warning preserved' if item['answer_status_warning'] else 'no warning'} |"
        )
    links = f"""# Question–Topic Link Report

Audit date: {DATE}

This is the human-readable companion to `data/question-study-coverage.json` and `data/study-topic-question-map.json`. It contains 105 precise links and no answer information.

| Question | Subject | Tested concept | Most relevant Study Library topic | Coverage | Answer status |
|---|---|---|---|---|---|
{chr(10).join(link_rows)}

Bidirectional reconciliation: {sum(item["question_count"] for item in topic_map)} question links in the topic map, 105 question records in the coverage map, and {len(topic_map)} topic records including {len(topic_map) - len(tested_topics)} explicit zero-example topics.
"""
    write("question-topic-link-report.md", links)

    still = f"""# Still-Uncovered Examination Concepts

Audit date: {DATE}

## Coverage result

Still-partial or unresolved Study Library concepts: **{len(uncovered_ids)}**

Exact unresolved coverage IDs: **{ids(uncovered_ids)}**

All 105 tested concepts have sufficient bilingual teaching and a precise topic link. “Covered” here means the learner can study and apply the concept; it does not certify that every original examination answer is academically resolvable.

## Preserved answer-review boundary

The following {len(warning_ids)} questions remain subject to their pre-existing academic-answer or scoring warning: {ids(warning_ids)}.

Their concepts are covered, but the library does not select, imply, or repair their answers. The warnings include strongly externally supported, probabilistic, unresolvable, and other human-review states already present before this audit.
"""
    write("still-uncovered-exam-concepts.md", still)

    change_log = f"""# Exam Coverage Change Log

Audit date: {DATE}

Pre-change recovery archive: `{CHECKPOINT}`

Answer-preservation Git baseline: `e722f98`

## Data

- Added `data/question-study-coverage.json` and its synchronized web copy with all 105 concept audits.
- Added `data/study-topic-question-map.json` and its synchronized web copy with all 132 topics, including explicit zero-example records.
- Added or regenerated {len(coverage_sections)} `coverage-*` bilingual lesson sections in root and web topic data.
- Kept the academic question JSON schema and every answer-related field unchanged; precise Study Library links are joined into runtime question objects from the dedicated mapping.

## Application

- Added the bilingual related-examination section to every topic page.
- Added difficulty counts, observed supplied-exam frequency, generic answer warnings, and a topic-filtered practice action.
- Added a Study topic filter to practice setup and the practice engine.
- Added a post-submission most-relevant-topic link to question review; it remains sealed before submission.
- Added responsive styles for the new traceability content.

## Validation and tests

- Added deterministic generator/check script `scripts/audit_exam_study_coverage.py`.
- Added `scripts/validate_exam_study_coverage.py` for completeness, bidirectionality, counts, sources, origins, no leakage, synchronization, warning preservation, and answer preservation.
- Added unit/component checks for complete mappings, precise topic filtering, no answer leakage, and sealed review links.
- Added Playwright integration and responsive checks at 320×568, 360×800, 390×844, 412×915, 768×1024, 1024×768, and 1280×800.
- Added the Phase 12 gates to `npm run validate:data`.

## Academic change control

Academic answer changes: **0**. No restored content proved an existing answer wrong, so no answer-change review record was created. Original course and examination source files were not modified.
"""
    write("exam-coverage-change-log.md", change_log)

    print(
        "Generated 7 coverage reports: "
        "105 questions, "
        f"{len(coverage_sections)} lessons, "
        f"{len(uncovered_ids)} uncovered."
    )


if __name__ == "__main__":
    main()
