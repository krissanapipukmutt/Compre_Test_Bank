# Language Display Test Report

**Validated:** 2026-07-31
**Result:** PASS

## Automated results

| Gate | Result |
| --- | --- |
| Phase 8 academic/data validator | PASS — 105 questions, 525 choices, 0 errors, 0 warnings |
| Translation-integrity validator | PASS — 105 questions, 525 choices, 0 errors, 0 warnings |
| Question-structure validator | PASS — 105 audited, 9 normalized, 0 structure-review |
| Phase 11 Study Library validator | PASS — 6 subjects, 44 chapters, 132 topics |
| Final readability validator | PASS — 132 complete topics, 0 duplicated question structure |
| Examination-to-Study coverage audit/validator | PASS — 105 links, 0 uncovered concepts, 0 errors, 0 warnings |
| ESLint | PASS |
| Strict TypeScript | PASS |
| Unit/component tests | PASS — 63/63 across 11 files |
| Playwright integration/responsive tests | PASS — 25/25 |
| Production build | PASS |
| Dependency audit at high severity | PASS — 0 vulnerabilities |

The production build generated `dist/index.html`,
`dist/assets/index-k7viNHTX.css`, and
`dist/assets/index-B7AkKklM.js`. Vite continues to report the existing
large-JavaScript-chunk advisory; it is not a functional or language-state
failure.

## New unit and component coverage

- Exact key and supported-value persistence for
  `compre-language-display-mode`.
- Safe fallback for invalid language values.
- Compatibility migration from the retired nested language preference without
  changing stored progress.
- Reset isolation from unrelated browser storage.
- Accessible compact control labels and `aria-pressed` state.
- Active-session serialization without question/choice dataset duplication.
- Exact restoration of session ID, question order, choice order, answer IDs,
  submitted IDs, current index, timer start, and duration.
- Blocking rejection of a corrupt choice order instead of reshuffling.
- Removal of the retired language field from progress preferences.

## Browser regression coverage

The dedicated `web/e2e/language-display.spec.ts` suite verifies:

1. Initial Mock display selection before starting.
2. English-only question and choices with Thai hidden.
3. Answer selection followed by bilingual switching.
4. Stable question ID, choice order, selected answer, submitted-answer state,
   current index, session ID, and timer origin.
5. Timer advancement without restart or pause.
6. No answer panel or correctness class before submission.
7. Repeated switching.
8. Switching after moving to another question.
9. Mode persistence on the final question.
10. Switching immediately before the final-submission dialog.
11. Results-page switching while reviewing a guaranteed incorrect answer.
12. Thai feedback hiding while English feedback remains.
13. Unchanged displayed score across Results switching.
14. Active-exam refresh recovery.
15. No question-text duplication in the active-session snapshot.
16. Individual Practice submission followed by bilingual study and
    English-only return.
17. 390×844 timed-exam mobile control sizing and non-overlap.
18. Study Library live switching and zero visible Thai language blocks in
    English-only mode.

The full existing browser suite also revalidated the supplied examination
visual viewer, missing-visual blocking, UNION table, diagram/table responsive
rendering, embedded statement ordering, topic depth, topic-to-question
coverage, long-question readability, answer sealing, judgment questions,
navigator/submission flow, and production asset responses.

## Responsive viewports

Existing and new browser tests cover:

- 320×568
- 360×800
- 390×844
- 412×915
- 768×1024
- 820×1180
- 1024×768
- 1280×800
- 1440×900

No tested document-level horizontal overflow, sticky-toolbar overlap, clipped
language control, or sub-44-pixel language target remains.

## Commands

```bash
cd /Users/krissanap/Document/KMUTT/COMPRE_CODEX/web
npm run check
npm run test:e2e
npm audit --audit-level=high
```
