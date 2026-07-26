# Task Register

Status: `[ ]` pending · `[~]` in progress · `[x]` completed · `[!]` blocked

- [x] **P0-01 · Phase 0 · Repository inventory and initialization**  
  Dependencies: project root access.  
  Expected output: control files, complete file inventory, course mapping, duplicate/unreadable/conflict reports.  
  Validation: every discovered file included; source hashes stable; JSON parses; IDs unique; uncertainties reported.
- [x] **P1-01 · Phase 1 · Bilingual academic knowledge base**  
  Dependencies: P0-01.  
  Expected output: subject/chapter/topic/glossary/source-reference data and bilingual subject documents.  
  Validation: schema and relationship checks; source coverage; low-confidence review coverage.
- [x] **P2-01 · Phase 2 · Bilingual examination question bank**  
  Dependencies: P1-01.  
  Expected output: questions, exam sets, source map, review status, evidence-backed explanations, quality reports.  
  Validation: IDs and references; bilingual completeness; answer-key integrity; evidence/status rules.
- [x] **P3-01 · Phase 3 · Academic and data-quality audit**  
  Dependencies: P1-01, P2-01.  
  Expected output: academic audit, data audit, and pre-web readiness status.  
  Validation: complete coverage audit and explicit severity classification.
- [x] **P4-01 · Phase 4 · Architecture and responsive UX design**  
  Dependencies: P3-01 readiness.  
  Expected output: ten architecture/requirements/design/test documents.  
  Validation: requirements traceability, data-model compatibility, responsive and accessibility criteria.
- [x] **P5-01 · Phase 5.1 · Web initialization and data validation**  
  Dependencies: P4-01.  
  Expected output: strict React/Vite/TypeScript project and runtime data validation.  
  Validation: lint, type check, unit tests, production build.
- [x] **P5-02 · Phase 5.2 · Responsive application shell**  
  Dependencies: P5-01.  
  Expected output: mobile-first navigation, routing, responsive layout, error/empty states.  
  Validation: shell tests, accessibility checks, lint, type check, build.
- [x] **P5-03 · Phase 5.3 · Study library**  
  Dependencies: P5-02.  
  Expected output: term/subject/chapter/topic/glossary/search/source-reference/bookmark views.  
  Validation: library/filter/render tests, Thai rendering, lint, type check, build.
- [x] **P5-04 · Phase 5.4 · Practice engine**  
  Dependencies: P5-03.  
  Expected output: filtering, randomization, feedback modes, review queues.  
  Validation: scoring/randomization/visibility/filter tests, lint, type check, build.
- [x] **P5-05 · Phase 5.5 · Mock examination**  
  Dependencies: P5-04.  
  Expected output: configuration, timer, navigator, submission, score and review.  
  Validation: timer/unanswered/no-leakage/scoring tests, lint, type check, build.
- [x] **P5-06 · Phase 5.6 · Progress and bookmarks**  
  Dependencies: P5-05.  
  Expected output: attempts, history, performance, weak topics, bookmarks, reset with local persistence.  
  Validation: persistence/bookmark/reset tests, lint, type check, build.
- [x] **P5-07 · Phase 5.7 · Responsive polish and accessibility**  
  Dependencies: P5-06.  
  Expected output: responsive, keyboard, contrast, reduced-motion, touch, safe-area refinements.  
  Validation: required viewport and accessibility tests.
- [x] **P5-08 · Phase 5.8 · Complete implementation verification**  
  Dependencies: P5-07.  
  Expected output: passing full suite and production bundle.  
  Validation: academic data, lint, type check, all automated tests, production build.
- [x] **P6-01 · Phase 6 · Final testing, audits, and release preparation**  
  Dependencies: P5-08.  
  Expected output: final reviews, screenshots, release readiness, README, final summary.  
  Validation: required commands and viewports complete; issues classified; completion state recorded.
- [x] **P7-01 · Phase 7 · Course recheck and external answer research**  
  Dependencies: P6-01 and pre-research backup.  
  Expected output: preserved original answer data; external-source and evidence datasets; probabilistic recommendations; five research reports; revised scoring and provenance UI.  
  Validation: Phase 7 provenance/preservation/link validator; JSON validation; lint; strict type check; 23 unit/integration tests; 6 browser tests; production build.

## EXAM-VISUAL-INTEGRITY

- [x] **P8-01 · Phase 8 · Complete examination visual-integrity audit and repair**  
  Dependencies: completed Phase 7 data and an immutable pre-visual-audit checkpoint.  
  Expected output: visual audit of all 105 questions; deterministic original-source assets; extended question schema; responsive accessible visual viewer; missing-visual scoring safeguards; five visual-integrity reports.  
  Validation: Phase 8 asset existence/safety/provenance/build and checkpoint-preservation validator passes with 0 errors and 0 warnings; lint and strict type check pass; 32/32 unit/integration tests and 10/10 browser tests pass; responsive diagram/table screenshots, modal/zoom/focus, broken-image, bilingual-alt, randomization, scoring-exclusion, and production-build gates pass.
- [x] **P8-02 · Phase 8 · Final independent question-visual verification**  
  Dependencies: P8-01 and immutable source/checkpoint baselines.  
  Expected output: second-pass verification of all 105 source mappings, trigger-word questions, every essential asset/crop, frontend order and safeguards, production packaging, and `reports/final-question-visual-verification.md`.  
  Validation: final source-boundary verifier passes 105 questions/16 pages with 0 errors; Phase 8 validation passes with 0 errors and 0 warnings; 32/32 unit/integration and 11/11 browser tests pass; responsive, blocking-warning, scoring, production build, and all 18 production-asset checks pass.

## BILINGUAL-TRANSLATION-INTEGRITY

- [x] **P9-01 · Phase 9 · Complete examination Thai-translation audit and repair**  
  Dependencies: completed Phase 8 question bank and immutable pre-translation checkpoint.  
  Expected output: contextual audit of all 105 questions, all choices and explanations; repaired natural Thai; terminology glossary; translation status metadata; five reports; bilingual frontend safeguards.  
  Validation: Phase 9 validator passes 105 questions/525 choices/24 glossary terms with 0 errors and 0 warnings; Phase 8 English/ID/order/answer and visual preservation passes; 40/40 unit/integration tests and 12/12 browser tests pass; all seven required bilingual viewports pass; production build and 18/18 production visual-asset checks pass; 0 dependency vulnerabilities.
