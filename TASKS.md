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

## VERCEL-PRODUCTION-DEPLOYMENT

- [x] **P10-01 · Phase 10 · Configure, deploy, and verify Vercel production**
  Dependencies: P9-01, passing production build, authenticated access to the existing `compre-test-bank` Vercel project.
  Expected output: explicit Vite deployment configuration under `web/`, ignored local Vercel metadata and credentials, successful production deployment, and `reports/vercel-production-deployment.md`.
  Validation: Vercel deployment `dpl_Fz6QMJniENF9nVSNUT5wT6PqeibL` is `Ready`; canonical URL returns HTTP 200 HTML; CSS and JavaScript return HTTP 200 with correct content types; the application renders and reloads its hash route without console, page, network, blank-page, overflow, or 404 failures; all 18 visual assets return HTTP 200 and match local SHA-256 hashes; immutable-data and translation validation, lint, strict type check, 40/40 unit/integration tests, 12/12 browser tests, and production build pass.

## STUDY-LIBRARY-ENRICHMENT

- [x] **P11-01 · Phase 11 · Enrich every subject, chapter, and topic**
  Dependencies: P10-01 and the pre-Phase-11 recoverable checkpoint.
  Expected output: structured bilingual objectives, overviews, lesson sections, terminology, comparisons, workflows, formulas where applicable, examples, misunderstandings, exam focus, quick review, and explicit source labels for all 6 subjects, 44 chapters, and 132 topics.
  Validation: Phase 11 validator passes 6 subjects, 44 chapters, 132 topics, and 176 supplementary chapter/topic lesson sections; every required bilingual structure and source label is present; course-material references resolve; no external content was added.

## QUESTION-STRUCTURE-NORMALIZATION

- [x] **P11-02 · Phase 11 · Audit and normalize embedded-choice questions**
  Dependencies: P11-01 data baseline and original examination page review.
  Expected output: raw-text preservation fields, normalized bilingual stems, structured embedded statement lines, stable selectable choices and answer keys, automated candidate detection, audit reports, and explicit human-review states.
  Validation: all 105 questions audited; 9/9 candidates compared with source pages 1, 2, and 4; raw English/Thai and all selectable choice and answer fields match the preservation baseline; 9 normalized, 0 display-only, 0 ambiguous, and 0 structure-review.

## BILINGUAL-READABILITY

- [x] **P11-03 · Phase 11 · Implement responsive bilingual lesson and question rendering**
  Dependencies: P11-01 and P11-02 validated data.
  Expected output: source-labelled topic reader, chapter/topic navigation, collapsible table of contents, glossary links, bookmarks, previous/next topic controls, reusable formatted-question component, and mobile-safe comparisons and typography.
  Validation: lint, strict TypeScript, 54/54 unit/component tests, 17/17 Playwright tests, and production build pass; all eight required viewports pass with no tested clipping, overlap, truncation, or document-level horizontal overflow; npm audit reports 0 vulnerabilities.

- [x] **P11-04 · Phase 11 · Final Study Library and question-readability audit**
  Dependencies: P11-01, P11-02, and P11-03.
  Expected output: corpus-wide topic depth, provenance, embedded-marker, duplication, raw-preservation, answer-preservation, bilingual ordering, typography, and responsive audit with `reports/final-study-and-question-readability-audit.md`.
  Validation: final readability validator passes all 132 topics and 105 questions with minimum structured content of 2,429 English/2,037 Thai characters, 9/9 marker-bearing questions normalized, 0 choice duplications, 0 raw failures, and 0 answer changes; lint, strict TypeScript, 54/54 unit/component tests, 17/17 browser tests, all eight required viewports, production build, and npm audit pass.

## EXAM-TO-STUDY-COVERAGE-AUDIT

- [x] **P12-01 · Phase 12 · Audit every examination concept against actual Study Library teaching**
  Dependencies: P11-04 and recoverable pre-coverage archive.
  Expected output: question-level tested concepts, skills, prerequisites, initial/final coverage quality, evidence origins, repairs, and exact unresolved coverage for all 105 questions.
  Validation: 105/105 records validate; initial audit distinguishes 57 missing, 21 keyword-only, 13 partial, 10 conflicting/uncertain, and 4 fully covered concepts; all source and evidence origins resolve; exact unresolved coverage is empty.
- [x] **P12-02 · Phase 12 · Add precise bidirectional question/topic mappings and bilingual teaching**
  Dependencies: P12-01.
  Expected output: `data/question-study-coverage.json`, `data/study-topic-question-map.json`, synchronized web data, and reusable source-labelled bilingual teaching repairs.
  Validation: 56 coverage lessons support 105 precise links across 44 directly tested topics; all 132 topic-map records reconcile; no learner-facing question IDs, choice IDs, answer keys, or answer explanations leak into teaching.
- [x] **P12-03 · Phase 12 · Add learner-facing topic traceability and filtered practice**
  Dependencies: P12-02.
  Expected output: bilingual related-examination topic section, counts, tested concepts, difficulty, observed frequency, generic warning state, topic-filtered practice, and sealed post-submission Study Library review links.
  Validation: topic practice returns only precise mapped questions; review links remain hidden before submission; zero-example topics avoid unsupported importance claims; all seven required responsive viewports have no tested document overflow.
- [x] **P12-04 · Phase 12 · Validate, report, and preserve academic answers**
  Dependencies: P12-01 through P12-03.
  Expected output: dedicated deterministic generator/validator, seven required reports, controls update, production build, and final recoverable Git checkpoint.
  Validation: Phase 8, translation, structure, Phase 11, readability, and Phase 12 validators pass; lint and strict TypeScript pass; 56/56 unit/component tests and 20/20 browser tests pass; production build succeeds; all answer-related fields match pre-audit Git baseline `e722f98`; 10 pre-existing answer warnings remain unchanged.

## LANGUAGE-DISPLAY-STATE-SAFETY

- [x] **P13-01 · Phase 13 · Implement an independent persistent language display**
  Dependencies: P12-04 and stable bilingual content.
  Expected output: exact `compre-language-display-mode` preference, bilingual and English-only modes, persistent desktop/mobile controls across Study, Practice, Mock, Results, and review, complete Thai visibility markup, and legacy preference normalization.
  Validation: the setting stores no answers or dataset; all visible Thai language blocks are hidden in English-only mode; English stays first in bilingual mode; accessible controls expose `English and Thai` and `English only` with 44-pixel targets.
- [x] **P13-02 · Phase 13 · Preserve active examination state across switching and refresh**
  Dependencies: P13-01 and existing stable question/choice IDs.
  Expected output: ID-only active-session snapshot and restore, stable randomization, timer effect isolation, and uninterrupted in-session switching.
  Validation: session ID, question/choice order, current and previous answers, submitted IDs, current index, timer start/duration, progress, and bookmarks remain unchanged by switching; corrupt snapshots block rather than reshuffle; refresh restores the same active session without copying academic wording.
- [x] **P13-03 · Phase 13 · Validate no leakage, responsive behavior, and Results switching**
  Dependencies: P13-01 and P13-02.
  Expected output: dedicated unit/component and Playwright regressions plus the three language-display reports.
  Validation: guaranteed-incorrect Results review, individual Practice feedback, repeated/final-question/pre-submit switching, no pre-submit answer panel or correctness class, mobile non-overlap, Study Library hiding, validators, lint, strict TypeScript, 63/63 unit/component tests, 25/25 browser tests, production build, and 0 dependency vulnerabilities all pass; no academic data or answer changed.
