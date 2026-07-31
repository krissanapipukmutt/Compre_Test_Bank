# Comprehensive Examination Study Application Plan

## Purpose

Transform all local Term 1 and Term 2 learning and examination materials into an evidence-backed bilingual study library, practice system, mock examination, and locally persisted progress experience.

## Scope and constraints

- Source roots: `TERM1/`, `TERM2/`, and academic files at repository root.
- Generated roots: `docs/`, `data/`, `reports/`, `scripts/`, and `web/`.
- Original academic files are immutable.
- Local processing only; no academic file or extracted content is sent to external services.
- English examination wording and choices are preserved.
- Academic uncertainty remains explicitly visible.
- Version 1 is a static React + Vite + TypeScript application with local JSON and browser storage.
- Mobile-first layouts cover phone, tablet, landscape, and desktop viewports.

## Phases, dependencies, and gates

1. **Phase 0 — inventory and initialization**  
   Dependency: accessible project root.  
   Gate: every discovered file inventoried, immutable-source baseline recorded, JSON valid, stable IDs unique, uncertain mappings reported.
2. **Phase 1 — academic content analysis**  
   Dependency: validated inventory.  
   Gate: subject/chapter/topic/source relationships valid; every subject has sources; low-confidence content reported.
3. **Phase 2 — examination analysis and bilingual answers**  
   Dependency: validated knowledge base.  
   Gate: stable question/choice IDs, bilingual fields, valid answer references, evidence on verified answers, ambiguous items retained.
4. **Phase 3 — academic and data-quality audit**  
   Dependency: Phases 1–2 data.  
   Gate: coverage, evidence, translations, references, schemas, and readiness independently audited.
5. **Phase 4 — architecture and responsive UX**  
   Dependency: readiness is `ready_for_web_development` or `ready_with_warnings`.  
   Gate: ten architecture documents agree with data models, flows, test strategy, and acceptance criteria.
6. **Phase 5 — implementation**  
   Dependency: validated architecture and academic data.  
   Gate per subphase: lint, type check, tests, and production build.
7. **Phase 6 — final testing and release**  
   Dependency: feature-complete application.  
   Gate: academic validation, automated tests, required viewport checks, accessibility/security review, and production build complete.
8. **Phase 7 — unresolved-answer course recheck and external research**  
   Dependency: Phase 6 release baseline and a safe pre-research backup.  
   Gate: every flagged answer receives one evidence origin; originals remain preserved; external sources and probabilities validate; scoring and post-submission evidence UI enforce the research policy.
9. **Phase 8 — examination visual-integrity audit and repair**  
   Dependency: Phase 7 evidence-preserving question bank and a safe pre-visual-integrity checkpoint.  
   Gate: every question is compared with its original page; essential visuals use source-faithful assets; missing/partial visual states are unscored and excluded from mock exams; accessible responsive rendering, asset provenance, production packaging, and preservation checks pass.
10. **Phase 9 — bilingual translation-integrity audit and repair**
    Dependency: Phase 8 visually complete question bank and a safe pre-translation checkpoint.
    Gate: all questions, choices, explanations, and terminology are contextually audited; incomplete translations remain blocked; English, answers, visuals, and historical translation evidence remain preserved.
11. **Phase 10 — Vercel production deployment**
    Dependency: Phase 9 validated production build and safe Vercel project access.
    Gate: the Vite application builds from `web/`, deploys to production, serves HTML/CSS/JavaScript and all referenced visual assets, renders without browser errors, and supports its hash routes on responsive viewports.
12. **Phase 11 — Study Library enrichment and question-structure normalization**
    Dependency: Phase 10 production baseline, recoverable pre-change checkpoint, and verified access to immutable course and examination sources.
    Gate: all subjects, chapters, and topics provide structured source-labelled bilingual learning content; every embedded-choice candidate is source-verified and preserves raw text, choice IDs, and answer keys; reusable responsive renderers, validators, reports, and all automated gates pass.
13. **Phase 12 — Examination-to-Study-Library coverage audit**
    Dependency: Phase 11 complete bilingual content, preserved question bank, and a recoverable pre-coverage checkpoint.
    Gate: all 105 questions are audited for the actual concept and skill tested; each has sufficient source-labelled bilingual teaching and a precise bidirectional topic link; topic-filtered practice and post-submission review links work without answer leakage; exact unresolved coverage is reported; academic answers remain unchanged; data, lint, strict TypeScript, unit/component, responsive browser, and production-build gates pass.
14. **Phase 13 — Independent language-display state and active-exam safety**
    Dependency: Phase 12 validated application and stable question/choice IDs.
    Gate: one persistent bilingual/English-only presentation preference works throughout Study, Practice, timed Mock, submission, Results, and review; switching never recreates or mutates the exam session; active refresh restores stable IDs/order/answers/timer origin without duplicating the dataset; answer sealing, mobile targets, responsive layouts, academic preservation, data, lint, strict TypeScript, unit/component, browser, dependency, and production-build gates pass.

## Phase 5 subphases

- 5.1 project initialization and runtime data validation
- 5.2 responsive application shell
- 5.3 study library
- 5.4 practice engine
- 5.5 mock examination
- 5.6 progress and bookmarks
- 5.7 responsive polish and accessibility
- 5.8 complete test and production build

## Decisions

- React + Vite + TypeScript is preferred because the application is local-first and statically deployable; no server-rendering requirement exists.
- Academic extraction and validation will use local scripts so results are reproducible and source files stay private.
- The existing Git repository is used for intentional release checkpoints; Git is never initialized implicitly.
- Vercel deploys the `web/` Vite application with Node 22, `npm install`, `npm run build`, and `dist` as the output directory.
- The application uses hash routing, so a server-side SPA catch-all rewrite is unnecessary.

## Discoveries

- The project root is accessible.
- An existing Git repository and the Vercel project `compre-test-bank` are available.
- Initial inspection found Term 1 and Term 2 trees, multiple office/PDF formats, source-code exercises, images, archives/installers, and a root `แนวข้อสอบ.pdf`.
- Course-code conflict risk exists in `TERM2/BIS603_BIS604 Bussiness Data Management` and requires document-content verification.

## Risks

- A large mixed-format corpus may contain image-only PDFs or diagrams that text extraction cannot fully interpret.
- Duplicate lecture exports (PDF/PPTX) and multiple student/work versions require cautious classification.
- Some examination answers may remain ambiguous if no supplied learning source is sufficiently direct.
- Legacy `.doc`, URL shortcuts, disk images, and archives may be unsupported academic extraction formats.

## Progress

- [x] Project root and Git status checked.
- [x] Required generated directories created.
- [x] Phase 0 inventory and initialization: 374 immutable sources inventoried and validated.
- [x] Phase 1: 6 subjects, 44 chapters, 132 topics, and 132 glossary entries validated.
- [x] Phase 2: 105 questions validated; 16 verified, 71 strongly inferred, and 18 review-required.
- [x] Phase 3: `ready_with_warnings`, with no structural errors.
- [x] Phase 4: ten architecture documents validated; React + Vite + strict TypeScript selected.
- [x] Phase 5: complete responsive application; lint/typecheck/build pass, 19 unit/integration tests and 5 browser tests pass.
- [x] Phase 6: academic, code, security, accessibility, responsive, test, build, preview, and release audits complete.
- [x] Phase 7: all 89 flagged questions rechecked; 33 newly course-verified, 47 externally verified, 2 strongly externally supported, 2 probability-only, and 5 unresolvable.
- [x] Phase 8: all 105 questions compared with all 16 original exam pages; 9 essential-visual questions repaired from embedded originals, 96 text-only questions confirmed complete, 18 source assets packaged, and no visual-loss review item remains.
- [x] Phase 8 final verification: all source boundaries, 48 wording triggers, 2 code-format items, 9 inline visuals, and 9 reference crops independently rechecked; one clipped Q79 supplemental reference crop repaired; no academic answer changed; final validators, 32 unit/integration tests, 11 browser tests, responsive checks, and production build pass.
- [x] Phase 9: all 105 questions and 525 choices contextually audited; translation validation, preservation checks, 40 unit/integration tests, 12 browser tests, responsive checks, and production build pass.
- [x] Phase 10: production deployment is ready at `https://compre-test-bank.vercel.app`; HTML, CSS, JavaScript, hash-route reload, responsive rendering, and all 18 visual assets verified.
- [x] Phase 11: all 6 subjects, 44 chapters, and 132 topics enriched; 105 questions audited and 9 source-verified embedded-statement questions normalized without answer changes; final topic-depth, provenance, duplication, bilingual-order, and preservation audit passes; 54 unit/component and 17 browser tests, eight-viewport readability review, production build, validators, and seven reports complete.
- [x] Phase 12: all 105 questions concept-audited; 57 missing, 21 keyword-only, 13 partial, 10 conflicting/uncertain, and 4 fully covered initial records repaired or confirmed through 56 grouped bilingual teaching sections; 105 precise links reconcile across 44 tested topics and all 132 topic-map records; 0 coverage concepts remain unresolved; 10 pre-existing academic-answer warnings and all answer data remain preserved.
- [x] Phase 13: one independently persisted bilingual/English-only display mode is available throughout the application, including timed exams and Results; stable active-session refresh preserves IDs, orders, answers, index, and timer origin without dataset duplication; answer sealing and all academic data remain unchanged; 63 unit/component and 25 browser tests, required responsive viewports, validators, dependency audit, and production build pass.

## Remaining work

No required Phase 13 language-display work remains. Human academic adjudication remains for the same 10 questions (2 strongly externally supported, 2 probability-only, 5 unresolvable, and the Q96 answer-key contradiction); these are answer-review issues, not language-display defects. Optional follow-up includes native-speaker Thai review, code-splitting, formal screen-reader checks, and independent Firefox/Safari certification.

## Recovery instructions

1. Read `AGENTS.md`, `TASKS.md`, and `PROJECT_STATE.md`.
2. Run the resume commands recorded in `PROJECT_STATE.md`.
3. Re-run the current phase validation before editing downstream data.
4. Compare immutable-source hashes in `data/file-inventory.json`; stop if an original changed unexpectedly.
5. If warnings are being addressed, select one from `reports/final-release-readiness.md`; otherwise the project is complete.
