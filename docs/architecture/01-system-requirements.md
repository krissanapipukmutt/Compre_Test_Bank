# System Requirements

## Product goal

Provide a private, local-first bilingual study and examination experience over the validated Term 1 and Term 2 datasets.

## Functional requirements

- **FR-01 Study library:** browse term → subject → chapter → topic; show English/Thai summaries, glossary, study aids, confidence, and source references.
- **FR-02 Search:** search English/Thai titles, summaries, terms, and question text.
- **FR-03 Bookmarks:** bookmark chapters and questions locally.
- **FR-04 Practice:** filter by term, subject, chapter, topic, difficulty, and answer status; randomize questions and choices without changing answer integrity.
- **FR-05 Feedback:** support immediate and delayed feedback; never reveal an answer before submission.
- **FR-06 Review queues:** review incorrect, bookmarked, and unanswered questions.
- **FR-07 Mock examination:** select subjects/count/timer, navigate questions, identify unanswered items, confirm submission, and score by subject/topic.
- **FR-08 Answer review:** display original English, Thai translation, learner answer, supported answer, bilingual explanations, every-choice explanations, evidence, confidence, status, and review warnings.
- **FR-09 Progress:** persist attempts, scores, history, bookmarks, weak topics, and reset confirmation in browser storage.
- **FR-10 Academic warnings:** clearly distinguish verified, inferred, ambiguous, and review-required data. Review-required questions are never scored.
- **FR-11 Data failure:** show a useful error screen if bundled academic JSON fails runtime validation.

## Non-functional requirements

- **NFR-01 Privacy:** no authentication, backend, telemetry, academic upload, or network dependency at runtime.
- **NFR-02 Portability:** static production output and relative bundled assets.
- **NFR-03 Integrity:** stable IDs; no answer keys by index; no answer leakage before submission.
- **NFR-04 Accessibility:** semantic HTML, keyboard operation, visible focus, appropriate labels/contrast, reduced motion, and 44×44 px touch targets.
- **NFR-05 Internationalization:** UTF-8, readable Thai line breaking, English originals preserved.
- **NFR-06 Responsive:** usable without unintended page-level horizontal overflow at every required viewport.
- **NFR-07 Quality:** TypeScript strict mode, runtime data validation, lint, unit/integration/responsive tests, and a passing production build.
- **NFR-08 Persistence resilience:** schema-versioned local storage with safe fallback for corrupt or unavailable storage.

## Academic constraints

- The English source question and choices are authoritative.
- `strongly_inferred` is never styled or described as verified.
- `requires_human_review` exposes no correct choice.
- Source references display repository-relative paths and page/slide locators.
- The BIS603 mapping warning remains visible on its subject page.

