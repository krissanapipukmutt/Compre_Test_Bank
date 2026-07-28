# Bilingual Readability Report

## Outcome

The Study Library and embedded-statement question layout pass at all eight required responsive viewports. English and Thai remain visually paired, embedded statements stay separate from selectable answers, tables use contained horizontal scrolling, and no tested page produces document-level horizontal overflow.

| Viewport | Coverage | Result |
| --- | --- | --- |
| 320×568 | Embedded statements, choices, Thai text, topic reader, overflow | PASS |
| 360×800 | Embedded statements, choices, Thai text, topic reader, overflow | PASS |
| 390×844 | Embedded statements, choices, Thai text, topic reader, overflow | PASS |
| 412×915 | Embedded statements, choices, Thai text, topic reader, overflow | PASS |
| 768×1024 | Embedded statements, choices, Thai text, topic reader, overflow | PASS |
| 1024×768 | Embedded statements, choices, Thai text, topic reader, overflow | PASS |
| 1280×800 | Embedded statements, choices, Thai text, topic reader, overflow | PASS |
| 1440×900 | Embedded statements, choices, Thai text, topic reader, overflow | PASS |

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
