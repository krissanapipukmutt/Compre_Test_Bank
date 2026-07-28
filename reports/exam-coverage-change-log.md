# Exam Coverage Change Log

Audit date: 2026-07-28

Pre-change recovery archive: `backups/pre-exam-to-study-coverage-audit-20260728T100551+0700.tar.gz`

Answer-preservation Git baseline: `e722f98`

## Data

- Added `data/question-study-coverage.json` and its synchronized web copy with all 105 concept audits.
- Added `data/study-topic-question-map.json` and its synchronized web copy with all 132 topics, including explicit zero-example records.
- Added or regenerated 56 `coverage-*` bilingual lesson sections in root and web topic data.
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
