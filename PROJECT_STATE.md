# Project State

- **Status:** COMPLETE_WITH_RESEARCH_WARNINGS
- **Current phase:** Phase 13 — Independent language-display state and active-exam safety
- **Current task:** P13-01 through P13-03 complete
- **Completed phases:** Phase 0, Phase 1, Phase 2, Phase 3, Phase 4, Phase 5, Phase 6, Phase 7, Phase 8, Phase 9, Phase 10, Phase 11, Phase 12, Phase 13
- **Last successful validation:** Phase 8 academic/data, Phase 9 translation, question structure, Phase 11 enrichment, final readability, and Phase 12 coverage validators pass with 0 errors and 0 warnings; lint and strict TypeScript pass; 63/63 unit/component tests and 25/25 browser tests pass; timed Mock switching, active refresh, individual Practice, Results review, Study Library, 44-pixel mobile targets, all existing responsive/visual/readability regressions, production build, and dependency audit pass; 0 academic data or answers changed
- **Last Git commit:** Phase 13 language-display state-safety checkpoint on `main` (see `git log -1`)
- **Last safe checkpoint:** Phase 10 Git release checkpoint; earlier recoverable archive remains at `backups/post-bilingual-translation-integrity-20260726T232800+0700.tar.gz`
- **Phase 11 pre-change checkpoint:** `backups/pre-study-library-enrichment-20260728T085454+0700.tar.gz`
- **Phase 12 pre-change checkpoint:** `backups/pre-exam-to-study-coverage-audit-20260728T100551+0700.tar.gz`
- **Production deployment:** `https://compre-test-bank.vercel.app` — Vercel deployment `dpl_Fz6QMJniENF9nVSNUT5wT6PqeibL`, status `Ready`
- **Research outcome:** 89 flagged questions reviewed; 33 newly verified from course materials; 47 verified externally; 2 strongly supported externally; 2 probability-based recommendations; 5 unresolvable
- **Visual-integrity outcome:** 105/105 questions manually audited and independently boundary-verified against 16 original pages; 48 wording triggers and 2 code-format items rechecked; 9 essential-visual questions complete; Q79 supplemental reference-crop cutoff repaired; 9 original embedded JPEGs and 9 lossless full-question reference PNGs packaged; 0 missing, partial, or visual-review questions; 0 academic answers changed
- **Translation-integrity outcome:** 105/105 questions and 525/525 choices audited; 104 question stems, 490 current choice translations, 490 preserved original-choice translations, 315 question explanation fields, 125 option explanations, and 49 external-evidence summaries repaired; 690 placeholder occurrences removed; 0 incomplete translations; 0 answer keys changed
- **Study Library outcome:** 6/6 subjects, 44/44 chapters, and 132/132 topics contain structured bilingual, source-labelled learning content; 552 total lesson sections include 452 topic sections after the coverage repair; 12 detailed chapter formulas and 19 topic formula records are available; 44 topics have precise supplied-exam links and 88 explicitly report that no supplied-exam example was found without implying unimportance
- **Question-structure outcome:** 105/105 questions audited; Q4, Q6, Q7, Q8, Q9, Q10, Q19, Q20, and Q28 source-verified and normalized; raw bilingual text, selectable choices, and every answer pointer preserved; 0 answer changes, 0 display-only cases, 0 ambiguous cases, and no unresolved structure IDs
- **Responsive-readability outcome:** reusable bilingual stem/statement rendering and full topic reader pass 320×568, 360×800, 390×844, 412×915, 768×1024, 1024×768, 1280×800, and 1440×900; comparison tables remain contained and tested pages have no horizontal document overflow
- **Final readability audit:** 132/132 topics exceed the structured-content floor (observed minimum 2,429 English/2,037 Thai characters); all nine marker-bearing questions render separate English and Thai statements and five answer cards on mobile and desktop; 0 summary-only topics, invalid provenance labels, choice duplications, raw-preservation failures, answer changes, or new review IDs
- **Exam-to-study coverage outcome:** 105/105 questions audited for tested concept, skill, prerequisites, and actual teaching depth; initial status was 57 missing, 21 keyword-only, 13 partial, 10 conflicting/uncertain, and 4 fully covered; 56 reusable bilingual lessons now support 105 precise links across 44 tested topics, while all 132 topics have explicit map records; final coverage is 49 course-supported, 49 authoritative-external-supported, and 7 explicitly supplementary; 0 concepts remain partial or unresolved
- **Exam traceability outcome:** every topic page shows the bilingual related-examination section with count, concepts, difficulty, supplied-exam frequency signal, filtered practice, and generic answer warning; question review links to the most relevant topic only after submission; the mapping stores no correct choice, answer explanation, or probability distribution
- **Language-display outcome:** one global `compre-language-display-mode` preference supports `bilingual` and `english_only` throughout Study, Practice, Mock, Results, and review; controls remain available during timed exams and preserve the current mode across questions and refresh; English remains first and all explicitly marked Thai content hides live in English-only mode
- **Active-exam safety outcome:** `compre-active-exam-session` stores stable IDs/order, answers, submitted IDs, index, timer origin/duration, and finish state without question/choice wording or dataset copies; language switching does not recreate the session or mutate exam state; refresh restores the exact active session; invalid choice order is rejected rather than reshuffled
- **Unresolved warnings:** 8 complete translations retain source-language review (Q22, Q23, Q32, Q35, Q60, Q63, Q69, Q92); 10 academic-answer records retain human review from Phase 7; BIS603 mapping warning; four historical external-reference endpoints resolve but reject automated requests with HTTP 403; production JS is 4.79 MB uncompressed / 354.25 KB gzip; formal screen-reader and non-Chromium certification not completed
- **Hard blockers:** none
- **Next action:** optional human adjudication of the same 10 flagged answer records, native-speaker language review, code-splitting, formal screen-reader review, or additional browser certification; no required language-display, coverage, automated, or deployment work remains

## Commands needed to resume

```bash
cd /Users/krissanap/Document/KMUTT/COMPRE_CODEX
.venv/bin/python scripts/validate_data.py --phase 8
.venv/bin/python scripts/validate_translation_integrity.py
.venv/bin/python scripts/validate_exam_visual_integrity.py
.venv/bin/python scripts/normalize_question_structure.py --check
.venv/bin/python scripts/validate_phase11.py
.venv/bin/python scripts/validate_final_readability.py
.venv/bin/python scripts/audit_exam_study_coverage.py --check
.venv/bin/python scripts/validate_exam_study_coverage.py
.venv/bin/python scripts/validate_external_research.py --check-links
cd web
npm run check
npm run test:e2e
npm audit --audit-level=high
```
