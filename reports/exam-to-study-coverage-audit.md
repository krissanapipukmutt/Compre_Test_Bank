# Exam-to-Study Coverage Audit

Audit date: 2026-07-28

Scope: all 105 supplied comprehensive-examination questions and all 132 Study Library topics

Recovery checkpoint: `backups/pre-exam-to-study-coverage-audit-20260728T100551+0700.tar.gz`

## Outcome

All 105 questions now have a precise, bidirectional link to concept teaching that is sufficient for guided bilingual self-study. The audit added or confirmed 56 grouped teaching sections across 45 directly tested topics. No question is marked complete merely because its text or choices exist.

- Current fully covered concepts: 105/105
- Still-partial or unresolved coverage: 0
- Precise question-to-topic links: 105
- Topics with supplied-exam evidence: 45/132
- Topics with no supplied-exam example: 87/132
- Preserved academic-answer warnings: 10
- Academic answers changed during this phase: 0

Exact unresolved coverage IDs: **None**

The 10 answer-warning records are not coverage failures. Their concepts are taught, while their pre-existing answer/scoring judgments remain visible and unchanged: question-comprehensive-022, question-comprehensive-023, question-comprehensive-035, question-comprehensive-039, question-comprehensive-046, question-comprehensive-063, question-comprehensive-064, question-comprehensive-088, question-comprehensive-092, question-comprehensive-096.

## Method

Each question was read as an assessment task, not accepted from tags alone. The audit recorded the tested concept, tested skill, prerequisite topics, initial coverage quality, evidence origin, precise Study Library topic, repair made, and final coverage quality. A question passes coverage only when a learner can find a bilingual definition or framework, discriminating rule or comparison, and guidance for applying the concept without seeing the answer.

The dedicated mapping deliberately excludes correct-answer IDs, correct-choice text, probability distributions, and answer explanations. Lesson repairs teach reusable concepts and never mention question IDs in learner-facing prose.

## Initial and final coverage

| Initial condition | Questions |
|---|---:|
| Fully covered | 4 |
| Partially covered | 13 |
| Keyword only | 21 |
| Conflicting or uncertain | 10 |
| Missing | 57 |

| Final evidence-backed condition | Questions |
|---|---:|
| Fully covered from supplied course evidence | 49 |
| Covered with authoritative external sources | 49 |
| Covered with explicitly labelled supplementary explanation | 7 |
| Still partial | 0 |
| Unresolved coverage | 0 |

## Subject coverage

| Subject | Questions audited | Initially needing repair | Currently fully covered |
|---|---:|---:|---:|
| BIS601 | 12 | 11 | 12 |
| BIS602 | 31 | 29 | 31 |
| BIS603 | 20 | 20 | 20 |
| BIS604 | 8 | 8 | 8 |
| BIS605 | 21 | 20 | 21 |
| BIS606 | 13 | 13 | 13 |

## Evidence controls

Evidence origins are explicit: course material 49, authoritative external 49, and supplementary explanation 7. External coverage resolves to records in `data/external-sources.json`; course coverage resolves to `data/source-references.json`. Supplementary sections are used for reasoning rules where the supplied item is under-specified or internally conflicting, and they do not silently adjudicate those answer records.

## Application traceability

Every topic page now includes “Related examination topics / หัวข้อที่เกี่ยวข้องกับแนวข้อสอบ,” including question count, bilingual tested concepts, difficulty distribution, a non-prevalence frequency signal, topic-filtered practice, and a generic answer-status warning where applicable. After answer submission, each question review links to its most relevant topic. No link is shown before submission.

## Verification gates

The Phase 12 validator checks 105/105 coverage records, all 132 topic-map records, bidirectional links, exact counts, evidence origins, source resolution, answer-warning consistency, learner-facing no-leakage rules, root/web data synchronization, and academic-answer preservation against Git checkpoint `e722f98`. Final project gates comprise data validation, lint, strict TypeScript checking, unit/component tests, Playwright browser tests at the seven required viewports, and the production build.
